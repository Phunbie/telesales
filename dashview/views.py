from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from teles.models import Agent
from .models import Feedback, Vote, Comment
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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



def country_data(country,collection, calls,Negotiation):
    collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
    total_paid_sum = collection[collection["Country"] == country]["Sum Total Paid"].astype(int).sum()
    #calls
    calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
    total_calls = calls[calls["Country"] == country]["Count Calls Connected"].astype(int).sum()
    #contact_rate
    #contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
   # contact = contact_rate[contact_rate["Country"] == country]["Contact Rate"].astype(float)
   # length = len(contact)
   # contact=contact.sum()/length 
   # contact = round(contact, 2)
    #Negotiation
    Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
    Negotiation_r = Negotiation[Negotiation["Country"] == country]["Negotiation Rate"].astype(float)
    length1 = len(Negotiation_r)
    Negotiation_r =  Negotiation_r.sum()/length1 
    Negotiation_r = round(Negotiation_r, 2)
    country_kpi=[total_calls, total_paid_sum, Negotiation_r]
    return country_kpi




def dashview(request):
    user= request.user
    username = user.username
    Country_features=[]
    countries = ['Uganda', 'Tanzania', 'Kenya','Nigeria','Togo','Malawi']
    country_data_range = ""
    
 

    if request.method == 'POST':
        if request.POST.get('country-data'):
            country_data_range = request.POST.get('country-data')
        if request.POST.get('message'):    
            message = request.POST.get('message')
            feedback = Feedback(
                user=user,
                text= message,
            )
            feedback.save()
            vote = Vote(user=user,feedback=feedback, value=False)
            vote.save()
    

    collection = bucket3('amount-collected-per-agent-mtd/')
    calls = bucket3('calls-per-agent-mtd/')
    #contact_rate = bucket3('contact-rate-per-agent-mtd/')
    Negotiation = bucket3('negotiation-rate-individual-mtd/')
    if country_data_range == 'WTD':
        collection = bucket3('amount-collected-per-agent/')
        calls = bucket3('calls-per-agent/')
        #contact_rate = bucket3('contact-rate-per-agent/')
        Negotiation = bucket3('negotiation-rate-individual/')



    for country in countries:
        count = country_data(country,collection, calls,Negotiation)
        count.append(country)
        Country_features.append(count)

    print(f"country-data {country_data_range}")
   
    votes = Vote.objects.all().order_by('-feedback_id') #.values()

    return render(request, 'dashview.html',{'username':username,'votes':votes,"Country_features":Country_features})

def upvote(request,uid):
    vote= Vote.objects.get(id=uid)
    feedbackid = vote.feedback.id
    feedback = Feedback.objects.get(id=feedbackid)
    if vote.value == True:
        vote.value = False
        feedback.totalvote = feedback.totalvote - 1
        vote.save()
        feedback.save()
    else:
        vote.value = True
        feedback.totalvote = feedback.totalvote + 1
        vote.save()
        feedback.save()
    data = 'success'
    return HttpResponse(status=204)

    #data = {'data':'success'}
    #response = JsonResponse(data,status=200)
    #return response
        

    