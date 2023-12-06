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
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


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


def query_date(data,date1,date2,user,data_col):
    data['Call Date'] = pd.to_datetime(data['Call Date'])
    mask = (data['User Name'] == user) & (data['Call Date'] >= pd.to_datetime(date1)) & (data['Call Date'] <= pd.to_datetime(date2))
    data = data[mask]
    data[data_col] = data[data_col].str.replace('%', '')
    data['Call Date'] = data['Call Date'].dt.strftime('%Y-%m-%d').str.replace('-', '/')
    data[data_col] = data[data_col].astype(float)
    dates =  data['Call Date']
    dates = dates.str[5:].tolist()
    datas =  data[data_col].tolist()
    return dates,datas
def query_date_country(data,date1,date2,country,data_col):
    data['Call Date'] = pd.to_datetime(data['Call Date'])
    mask = (data['Country'] == country) & (data['Call Date'] >= pd.to_datetime(date1)) & (data['Call Date'] <= pd.to_datetime(date2))
    first_res = data[mask]
    first_res[data_col] = first_res[data_col].str.replace('%', '')
    first_res[data_col] = first_res[data_col].astype(float)
    final_res=first_res.groupby('Call Date')[data_col].mean().reset_index()
    final_res['Call Date'] = final_res['Call Date'].dt.strftime('%Y-%m-%d').str.replace('-', '/')
    final_res['Call Date'] = final_res['Call Date'].str[5:]
    dates =  final_res['Call Date'].tolist()
    datas =  final_res[data_col].tolist()
    return dates,datas


    
  


def report(request):
    user = request.user
    agent =  Agent.objects.get(user=user)
    username = request.user.username
    username = username.capitalize()
    first_name = agent.first_name
    last_name =  agent.last_name
    country = agent.country
    user_name = first_name.strip() + " " + last_name.strip()

    collection = bucket3('amount-collected-per-agent-mtd/')
    collection = collection.sort_values(by='Call Date')
    calls = bucket3('calls-per-agent-mtd/')
    calls = calls.sort_values(by='Call Date')
    contact_rate = bucket3('contact-rate-per-agent-mtd/')
    contact_rate = contact_rate.sort_values(by='Call Date')
    Negotiation = bucket3('negotiation-rate-individual-mtd/')
    Negotiation = Negotiation.sort_values(by='Call Date')
    name_list = collection['User Name'].unique().tolist()
    kpis_dict = {"collection":collection,"calls":calls,"Negotiation":Negotiation}
    kpi_essential_column = {"collection":"Sum Total Paid","calls":"Count Calls Connected","Negotiation":"Negotiation Rate"}

    kpi = ""
    call_Agents = ""
    date_from = ""
    date_to = ""
    compare_df = ""
    user_df = ""

    if request.method == 'POST':
        kpi = request.POST.get('kpis')
        call_Agents = request.POST.get('compare')
        date_from = request.POST.get('from')
        date_to = request.POST.get('to')
        call_agent_lists = query_date(kpis_dict[kpi],date_from,date_to,call_Agents,kpi_essential_column[kpi])
        if user_name not in name_list:
            user_df =  query_date_country(kpis_dict[kpi],date_from,date_to,country,kpi_essential_column[kpi])
        else:
            user_df =  query_date(kpis_dict[kpi],date_from,date_to,user_name,kpi_essential_column[kpi])
        #print(date_from,date_to,Agent)
        print("usertest",user_df[1])
        print("usertest",user_df[0])
        print("usertesta",call_agent_lists[1])
        print("usertesta",call_agent_lists[0])
  

    
    min_date = contact_rate['Call Date'].unique().tolist()[0]
    max_date = contact_rate['Call Date'].unique().tolist()[-1]
    #username = request.user.username
    name_list =  [x for x in name_list if x is not None]
    #print(name_list)
   # name_list = json.dumps(name_list)
    return render(request, 'report.html',{'username':username,"name_list":name_list,"min_date":min_date,"max_date":max_date}) 



