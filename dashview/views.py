from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from teles.models import Agent
from .models import Comment,Feedbacknew
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import boto3
import json
import pandas as pd
from django.db.models import Q
from datetime import datetime, timedelta

  


def get_latest_week_data(df):
  # Ensure "Call Date" is in datetime format
  df['Call Date'] = pd.to_datetime(df['Call Date'])

  # Get the current date
  current_date = datetime.now()

  # Calculate the start and end dates of the current week
  start_of_current_week = current_date - timedelta(days=current_date.weekday())
  end_of_current_week = start_of_current_week + timedelta(days=6)
 

  # Calculate the start and end dates of the previous week
  start_of_previous_week = start_of_current_week - timedelta(weeks=1)
  end_of_previous_week = end_of_current_week - timedelta(weeks=1)
  print(start_of_previous_week)
  latest_week_data = df[(df['Call Date'] >= start_of_current_week) & (df['Call Date'] <= end_of_current_week)]
  if len(latest_week_data) >= 1:
      return latest_week_data
  else:
      # If there is no data for the current week, get the previous week's data
      previous_week_data = df[(df['Call Date'] >= start_of_previous_week) & (df['Call Date'] <= end_of_previous_week)]
      return previous_week_data

def get_latest_month_data(df):
   # Ensure "Call Date" is in datetime format
   df['Call Date'] = pd.to_datetime(df['Call Date'])

   # Get the current year and month
   current_year = datetime.now().year
   current_month = datetime.now().month

   # Calculate the previous year and month
   previous_year = current_year if current_month > 1 else current_year - 1
   previous_month = current_month - 1 if current_month > 1 else 12

   # Try to get the current month's data
   try:
       latest_month_data = df[(df['Call Date'].dt.year == current_year) & (df['Call Date'].dt.month == current_month)]
       return latest_month_data
   except:
       # If there is no data for the current month, get the previous month's data
       previous_month_data = df[(df['Call Date'].dt.year == previous_year) & (df['Call Date'].dt.month == previous_month)]
       return previous_month_data



def transforn_merge(df1,df2):
    df2 = df2.drop(columns=["Sum Variable Pay Amount Earned"])

    # Step 2: Rename the columns
    df2 = df2.rename(columns={"Call Date Date": "Call Date", "Updated Fullname":"User Name", "Total Amount Paid": "Sum Total Paid"})

    # Step 3: Merge the two DataFrames using an outer join
    merged_df = pd.concat([df1, df2])
    merged_df['User Name'] = merged_df['User Name'].str.strip()
    return merged_df


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
    # contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
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
    feedbacks= Feedbacknew.objects.filter(user=user).order_by('date')
    feedbacks = feedbacks[::-1]
    agents= Agent.objects.get(user=user)
    firstname = agents.first_name.strip()
    lastname = agents.last_name.strip()
    agent_username = firstname + " " + lastname
    #print(firstname,lastname, agent_username)
    #general_feedback = Feedbacknew.objects.filter(agent="all").order_by('-date')
    #agent_feedback = Feedbacknew.objects.filter(agent=agent_username).order_by('-date')
    agent_feedback = Feedbacknew.objects.filter(Q(agent=agent_username) | Q(agent='all')).order_by('-date')
    username = user.username
    Country_features=[]
    countries = ['Uganda', 'Tanzania', 'Kenya','Nigeria','Togo','Malawi']
    country_data_range = ""


    collection1_year = bucket3('amount-collected-per-agent-mtd/')
    collection2_year = bucket3('vicidial-mtd/')
    collection_year = transforn_merge( collection1_year,collection2_year)
    collection_year = collection_year.sort_values(by='Call Date')
    calls_year = bucket3('calls-per-agent-mtd/')
    calls_year = calls_year.sort_values(by='Call Date')
    contact_rate_year = bucket3('contact-rate-per-agent-mtd/')
    contact_rate_year = contact_rate_year.sort_values(by='Call Date')
    Negotiation_year = bucket3('negotiation-rate-individual-mtd/')
    Negotiation_year = Negotiation_year.sort_values(by='Call Date')
    ATT_year = bucket3('calls-per-agent-mtd/')
    ATT_year = ATT_year.sort_values(by='Call Date')

    
    collection1 = bucket3('amount-collected-per-agent-mtd/')
    collection2 = bucket3('vicidial-mtd/')
    collection = transforn_merge(collection1,collection2)
    collection = collection.sort_values(by='Call Date')
    #collection = bucket3('amount-collected-per-agent-mtd/')
    name_list = collection['User Name'].unique().tolist()
    calls = bucket3('calls-per-agent-mtd/')
    is_agent = agent_username in  name_list

    if request.method == 'POST':
        if request.POST.get('country-data'):
            country_data_range = request.POST.get('country-data')
        if request.POST.get('feedback'):
            agent_name = request.POST.get('agent_name')  
            if  agent_name not in name_list:
                agent_name = "all"
            message = request.POST.get('feedback')
            feedback = Feedbacknew(
                user=user,
                text= message,
                agent = agent_name
            )
            feedback.save()
    
    

    #collection = bucket3('amount-collected-per-agent-mtd/')
    #name_list = collection['User Name'].unique().tolist()
    #calls = bucket3('calls-per-agent-mtd/')
    #contact_rate = bucket3('contact-rate-per-agent-mtd/')
    Negotiation = bucket3('negotiation-rate-individual-mtd/')
    if country_data_range == 'WTD':
        collection1 = bucket3('amount-collected-per-agent/')
        collection2 = bucket3('vicidial-data/')
        collection = transforn_merge( collection1,collection2)
        collection = collection.sort_values(by='Call Date')
        #collection = bucket3('amount-collected-per-agent/')
        calls = bucket3('calls-per-agent/')
        #contact_rate = bucket3('contact-rate-per-agent/')
        Negotiation = bucket3('negotiation-rate-individual/')



    for country in countries:
        count = country_data(country,collection, calls,Negotiation)
        count.append(country)
        Country_features.append(count)

    print(f"country-data {country_data_range}")
   
    #votes = Vote.objects.all().order_by('-feedback_id') #.values()

    return render(request, 'dashview.html',{'username':username,"Country_features":Country_features,
                                            "feedbacks":feedbacks,"agent_feedback":agent_feedback,"name_list":name_list,"is_agent":is_agent,#"general_feedback": general_feedback,
                                            "user_is_supervisor": request.user.groups.filter(name="Supervisor").exists()})


def feedback_comment(request,f_id):
    user= request.user
    username = user.username
    feedback= Feedbacknew.objects.get(id=f_id)
    comments = Comment.objects.filter(feedback=feedback)
    if request.method == 'POST':
        reply = request.POST.get('replies')
        add_comment = Comment(text=reply,feedback=feedback,user=user)
        add_comment.save()

    return render(request,'reply.html',{"comments":comments,"username":username,"feedback":feedback})
    



"""

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
  """      

    