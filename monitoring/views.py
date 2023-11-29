from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from teles.models import Agent
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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

def monitor(request):
    user = request.user
    agent= Agent.objects.get(user=user)
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


    user_name = first_name.strip() + " " + last_name.strip()
    if  user_name not in user_list:
        user_name = "Wilson Mukobeza"
        #user_name = "Adeola Adebayo"
    print(user_name) 
    #user_name = "Wilson Mukobeza"
    #user_name = "Adeola Adebayo"
    #user_name = "Mercy Atieno"
    #collection
    collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
    total_paid_sum = collection[collection["User Name"] == user_name]["Sum Total Paid"].astype(int).tolist()
    length_paid = len(total_paid_sum) -1
    latest_paid = total_paid_sum[length_paid]
    #print(f"The sum total paid for {user_name} is: {total_paid_sum}")
    #calls
    calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
    total_calls = calls[calls["User Name"] == user_name]["Count Calls Connected"].astype(int).tolist()
    length_call = len(total_calls) -1
    latest_call = total_calls[length_call]
    #contact_rate
    contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
    contact = contact_rate[contact_rate["User Name"] == user_name]["Contact Rate"].astype(float).tolist()
    length_contact = len(contact) - 1
    latest_contact = contact[length_contact]
    #contact = round(contact, 2)
    #Negotiation
    Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
    Negotiation_r = Negotiation[Negotiation["User Name"] == user_name]["Negotiation Rate"].astype(float).tolist()
    length_negotiotion = len(Negotiation_r) - 1
    latest_negotiation = Negotiation_r[length_negotiotion]
    #Negotiation_r = round(Negotiation_r, 2)
    input_list = {"total_paid_sum":total_paid_sum,
                   "total_calls":total_calls,
                   "contact":contact,
                   "Negotiation":Negotiation_r,"latest_paid":latest_paid,
                   "latest_call":latest_call,
                   "latest_contact":latest_contact,
                   "latest_negotiation":latest_negotiation, "first_name":first_name, "last_name":last_name}
    #input_list = json.dumps(input_list)

    return render(request, 'monitor.html', {'username': username,'agent':agent,"input_list":input_list})


def monitorapi(request):
    if request.user.is_authenticated:
        user = request.user
        agent= Agent.objects.get(user=user)
        country = agent.country
        role = agent.role
        first_name = agent.first_name
        last_name =  agent.last_name
    
    collection = bucket3('amount-collected-per-agent/')
    calls = bucket3('calls-per-agent/')
    contact_rate = bucket3('contact-rate-per-agent/')
    Negotiation = bucket3('negotiation-rate-individual/')


    #user_name = first_name + " " + last_name 
    #user_name = "Wilson Mukobeza"
    user_name = "Adeola Adebayo"
    #collection
    collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
    total_paid_sum = collection[collection["User Name"] == user_name]["Sum Total Paid"].astype(int).tolist()
    #print(f"The sum total paid for {user_name} is: {total_paid_sum}")
    #calls
    calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
    total_calls = calls[calls["User Name"] == user_name]["Count Calls Connected"].astype(int).tolist()
    #contact_rate
    contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
    contact = contact_rate[contact_rate["User Name"] == user_name]["Contact Rate"].astype(float).tolist()
    length = len(contact)
    #contact = round(contact, 2)
    #Negotiation
    Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
    Negotiation_r = Negotiation[Negotiation["User Name"] == user_name]["Negotiation Rate"].astype(float).tolist()
    length1 = len(Negotiation_r)
    #Negotiation_r = round(Negotiation_r, 2)
    S3_dict = {"collection":total_paid_sum, "calls":total_calls,"contact_rate": contact,"Negotiation": Negotiation_r }
    #S3_dict = json.dumps(S3_dict)


    data =  S3_dict
    response = JsonResponse(data,status=200)
    return response