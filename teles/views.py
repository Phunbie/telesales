from django.shortcuts import render, redirect
from django.contrib.auth.models import User
#from django.contrib.auth import login,authenticate, logout
from .models import Agent
from authentication.views import logIn
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import vicidata
import boto3
import json
import pandas as pd


def bucket3(folder):
    s3 = boto3.resource(
                's3',
                aws_access_key_id='AKIAXTPIUFRUHESZIQNU',
                aws_secret_access_key='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',
            )
    bucket = s3.Bucket('telecollection-app')

    folder_prefix = folder

    #Get the latest object (file) in the "public" folder
    latest_object = max(bucket.objects.filter(Prefix=folder_prefix),
                        key=lambda obj: obj.last_modified)
    body = latest_object.get()['Body'].read().decode('utf-8')
    data = json.loads(body)
    data = pd.DataFrame(data)
    return data


def home(request):
    #users = User.objects.all()
    if request.user.is_authenticated:
        user = request.user
        agent= Agent.objects.get(user=user)
        email = agent.user.email
        angaza_id = agent.angaza_id
        country = agent.country
        role = agent.role
        username = request.user.username
        username = username.capitalize()
        first_name = agent.first_name
        last_name =  agent.last_name

        collection = bucket3('amount-collected-per-agent/')
        collection = collection.sort_values(by='Call Date')
        calls = bucket3('calls-per-agent/')
        calls = calls.sort_values(by='Call Date')
        contact_rate = bucket3('contact-rate-per-agent/')
        contact_rate = contact_rate.sort_values(by='Call Date')
        Negotiation = bucket3('negotiation-rate-individual/')
        Negotiation = Negotiation.sort_values(by='Call Date')
        user_list= collection['User Name'].unique().tolist()


        combined_list = ""
        list_name = []
        list_collection =[]
        list_call = []
        list_contact = []
        list_negotiation =[]
        for i, user_name in enumerate(user_list):
            collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
            total_paid_sum = collection[collection["User Name"] == user_name]["Sum Total Paid"].astype(int).sum()
            #calls
            calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
            total_calls = calls[calls["User Name"] == user_name]["Count Calls Connected"].astype(int).sum()
            #contact_rate
            contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
            contact = contact_rate[contact_rate["User Name"] == user_name]["Contact Rate"].astype(float)
            length = len(contact)
            contact=contact.sum()/length 
            contact = round(contact, 2)
            #Negotiation
            Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
            Negotiation_r = Negotiation[Negotiation["User Name"] == user_name]["Negotiation Rate"].astype(float)
            length1 = len(Negotiation_r)
            Negotiation_r =  Negotiation_r.sum()/length1 
            Negotiation_r = round(Negotiation_r, 2)
            
            list_name.append(user_name)
            
            list_collection.append(total_paid_sum)
            
            list_call.append(total_calls)
            
            list_contact.append(contact)
            
            list_negotiation.append(Negotiation_r)
            if i == 4:
                combined_list = list(zip(list_name, list_collection, list_call, list_contact, list_negotiation))
                break


        #print(f"user list:{combined_list}")

        
        user_name = first_name.strip() + " " + last_name.strip() 
        if  user_name not in user_list:
            user_name = "Wilson Mukobeza"
            #user_name = "Adeola Adebayo"
        #collection
        collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
        total_paid_sum = collection[collection["User Name"] == user_name]["Sum Total Paid"].astype(int).tolist()
        collection_increase = total_paid_sum[-1] -  total_paid_sum[-2]
        collection_increase = collection_increase >= 0
        total_paid_sum = total_paid_sum[-1]
        #print(f"The sum total paid for {user_name} is: {total_paid_sum}")
        #calls
        calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
        total_calls = calls[calls["User Name"] == user_name]["Count Calls Connected"].astype(int).tolist()
        calls_increase= total_calls[-1] - total_calls[-2]
        calls_increase= calls_increase >= 0
        total_calls = total_calls[-1]
        #contact_rate
        contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
        contact = contact_rate[contact_rate["User Name"] == user_name]["Contact Rate"].astype(float).tolist()
        contact_increase = contact[-1] - contact[-2]
        contact_increase = contact_increase >= 0
        contact = contact[-1]
        #length = len(contact)
        #contact=contact.sum()/length 
        contact = round(contact, 2)
        #Negotiation
        Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
        Negotiation_r = Negotiation[Negotiation["User Name"] == user_name]["Negotiation Rate"].astype(float).tolist()
        Negotiation_increase =  Negotiation_r[-1] - Negotiation_r[-2]
        Negotiation_increase = Negotiation_increase >= 0
        Negotiation_r = Negotiation_r[-1]
        #length1 = len(Negotiation_r)
        #Negotiation_r =  Negotiation_r.sum()/length1 
        Negotiation_r = round(Negotiation_r, 2)
        #print(f"The sum total rate for {user_name} is: {Negotiation_r}")
        kpi_increment_list = [collection_increase,calls_increase,contact_increase, Negotiation_increase]


        context = {'username': username,
                   'email':email,
                   'agent':agent,
                   'angaza_id':angaza_id,
                   'country':country,
                   'role':role,
                   "total_paid_sum": total_paid_sum,
                   "total_calls":total_calls,
                   "contact":contact,
                   "negotiation_r":Negotiation_r,
                   "combined_list": combined_list
                   }
        
        return render(request, 'index.html',context )
    return redirect(logIn) 


def dataapi(request):
        stat = vicidata.status()
        data = {'data':stat}
        response = JsonResponse(data,status=200)
        return response

def agentlist(request):
    list = vicidata.agent_list()
    username = request.user.username
    username = username.capitalize()
    return render(request, 'agents.html', {'username': username,'list':list})


def callsapi(request):
    stat = vicidata.calls()
    data = {'data':stat}
    response = JsonResponse(data,status=200)
    return response


@login_required
def profile(request):
    user = request.user
    agent= Agent.objects.get(user=user)
    email = agent.user.email
    angaza_id = agent.angaza_id
    country = agent.country
    role = agent.role
    username = request.user.username
    username = username.capitalize()
    return render(request, '2ndProfile.html', {'username': username,'email':email,'agent':agent,'angaza_id':angaza_id,'country':country,'role':role})



@login_required
def dashboard(request):
    username = request.user.username
    username = username.capitalize()
    return render(request, 'dashboard.html', {'username': username})

def monitor(request):
    user = request.user
    agent= Agent.objects.get(user=user)
    email = agent.user.email
    angaza_id = agent.angaza_id
    country = agent.country
    role = agent.role
    username = request.user.username
    username = username.capitalize()
    return render(request, 'monitor.html', {'username': username,'email':email,'agent':agent,'angaza_id':angaza_id,'country':country,'role':role})





def agent_info(request, id):
    data = vicidata.agentInfo(id)
    username = request.user.username
    username = username.capitalize()
    return render(request, 'agent.html', {'username': username, 'data':data})





@login_required
def editProfile(request):
    user = request.user
    username = user.username
    agent= Agent.objects.get(user=user)
    email = agent.user.email
    angaza_id = agent.angaza_id
    country = agent.country
    role = agent.role
    if request.method == 'POST':
        # Get the user data from the request.
        username = request.POST.get('uname')
        role = request.POST.get('role')
        email = request.POST.get('email')
        country = request.POST.get('country')
        angaza_id = request.POST.get('angaz')

        user.username = username
        user.email = email
        agent.role = role
        agent.country = country
        agent.angaza_id = angaza_id
        user.save() 
        agent.save()
        messages.success(request,f'Account Updated')
        return redirect(profile)


    return render(request, 'profile_edit.html', {'username': username,'email':email,'angaza_id':angaza_id,'country':country,'role':role})



def password(request):
    return render(request, 'password.html')
