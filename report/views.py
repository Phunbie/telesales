from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from teles.models import Agent
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import boto3
import json
import pandas as pd
import warnings
import csv

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
    data[data_col] = data[data_col].str.replace(',', '')
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
    first_res[data_col] = first_res[data_col].str.replace(',', '')
    first_res[data_col] = first_res[data_col].astype(float)
    final_res=first_res.groupby('Call Date')[data_col].mean().reset_index()
    final_res['Call Date'] = final_res['Call Date'].dt.strftime('%Y-%m-%d').str.replace('-', '/')
    final_res['Call Date'] = final_res['Call Date'].str[5:]
    dates =  final_res['Call Date'].tolist()
    datas =  final_res[data_col].tolist()
    return dates,datas


def query_date_global(data,date1,date2,data_col):
    data['Call Date'] = pd.to_datetime(data['Call Date'])
    mask = (data['Call Date'] >= pd.to_datetime(date1)) & (data['Call Date'] <= pd.to_datetime(date2))
    first_res = data[mask]
    first_res[data_col] = first_res[data_col].str.replace('%', '')
    first_res[data_col] = first_res[data_col].str.replace(',', '')
    first_res[data_col] = first_res[data_col].astype(float)
    final_res=first_res.groupby('Call Date')[data_col].mean().reset_index()
    final_res['Call Date'] = final_res['Call Date'].dt.strftime('%Y-%m-%d').str.replace('-', '/')
    final_res['Call Date'] = final_res['Call Date'].str[5:]
    dates =  final_res['Call Date'].tolist()
    datas =  final_res[data_col].tolist()
    return dates,datas


def list_name_in_country(country,data):
    res = data[data['Country']==country]["User Name"].unique().tolist()
    return res


    
  


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
    all_name_list = collection['User Name'].unique().tolist()
    name_list = list_name_in_country(country,collection)
    kpis_dict = {"collection":collection,"calls":calls,"Negotiation":Negotiation}
    kpi_essential_column = {"collection":"Sum Total Paid","calls":"Count Calls Connected","Negotiation":"Negotiation Rate"}
    kpi_essential_column2 = {"collection":"Collection","calls":"Calls Connected","Negotiation":"Negotiation Rate"}
    is_super = user.groups.filter(name="Supervisor").exists()
    permitted = user_name in  all_name_list or is_super
    min_date = contact_rate['Call Date'].unique().tolist()[0]
    max_date = contact_rate['Call Date'].unique().tolist()[-1]
    start_date = contact_rate['Call Date'].unique().tolist()[0]
    end_date = contact_rate['Call Date'].unique().tolist()[-1]


    kpi = ""
    call_Agents = ""
    date_from = ""
    date_to = ""
    compare_df = ""
    user_df = ""
    
    default_data_collection = query_date_country(collection, min_date,max_date,country,"Sum Total Paid")
    global_collection = query_date_global(collection, min_date,max_date,"Sum Total Paid")
    your_collection = query_date(collection,min_date,max_date,user_name,"Sum Total Paid")
    current_kpi = "Collection"
    user_dates =  default_data_collection[0]
    user_dates =  json.dumps(user_dates)
    user_datas =  default_data_collection[1]
    user_title = "Country"
    if user_name  in all_name_list:
        user_dates =  your_collection[0]
        user_dates =  json.dumps(user_dates)
        user_datas =  your_collection[1]
        user_title = "your"

   
    other_dates =  default_data_collection[0]
    other_dates =  json.dumps(other_dates)
    other_datas =  default_data_collection[1]
    other_title = "country"

   #third_dates =  other_dates
    #third_datas =  other_datas
    #if user_name  not in all_name_list:
    third_dates =  global_collection[0]
    third_dates =  json.dumps(third_dates)
    third_datas =  global_collection[1]
    third_title = "Global"

    
    call_Agents = "country"
    if request.method == 'POST':
        kpi = request.POST.get('kpis')
        current_kpi = kpi_essential_column2[kpi]
        call_Agents = request.POST.get('compare')
        date_from = request.POST.get('from')
        date_to = request.POST.get('to')
        csv_checkbox = request.POST.get("coc")
        start_date = date_from 
        end_date = date_to
        call_agent_lists = query_date(kpis_dict[kpi],date_from,date_to,call_Agents,kpi_essential_column[kpi])
        third_df =  query_date_country(kpis_dict[kpi],date_from,date_to,country,kpi_essential_column[kpi])
        other_title = call_Agents
        third_title = "Country"
        if user_name not in name_list:
            user_df =  query_date_country(kpis_dict[kpi],date_from,date_to,country,kpi_essential_column[kpi])
            third_df =  query_date_global(kpis_dict[kpi], date_from,date_to,kpi_essential_column[kpi])
            third_title = "Global"
        else:
            user_df =  query_date(kpis_dict[kpi],date_from,date_to,user_name,kpi_essential_column[kpi])
        #download csv 
        if  csv_checkbox=="report":
            report_dictionary= {'user_date':user_df[0],user_name:user_df[1] }  # ,'compare_date':call_agent_lists[0] ,call_Agents:call_agent_lists[1]
            comparision_dictionary = {'compare_date':call_agent_lists[0] ,call_Agents:call_agent_lists[1]}
            df = pd.DataFrame.from_dict(report_dictionary)
            csv_file = df.to_csv(index=False)
            response = HttpResponse(csv_file,content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{kpi_essential_column[kpi]}.csv"'
           
           # writer = csv.writer(response)

            #  Write the header row
           # writer.writerow(['user_date', user_name,'compare_date', call_Agents])

            # Write the data rows
            #writer.writerow(['Row 1 Data 1', 'Row 1 Data 2', 'Row 1 Data 3'])
            #writer.writerow(['Row 2 Data 1', 'Row 2 Data 2', 'Row 2 Data 3'])

            return response
        
        user_dates = user_df[0]
        user_dates = json.dumps(user_dates)
        user_datas = user_df[1]
       # user_datas =  json.dumps(user_datas)
        other_dates = call_agent_lists[0]
        other_dates = json.dumps(other_dates)
        other_datas = call_agent_lists[1]
       # other_datas = json.dumps(other_datas)
        third_dates =  third_df[0]
        third_dates =  json.dumps(third_dates)
        third_datas =  third_df[1]
   
     
    #min_date = contact_rate['Call Date'].unique().tolist()[0]
    #max_date = contact_rate['Call Date'].unique().tolist()[-1]
    #username = request.user.username
    name_list =  [x for x in name_list if x is not None]
    #print(name_list)
   # name_list = json.dumps(name_list)
   
    return render(request, 'report.html',{'username':username,"name_list":name_list,"min_date":min_date,
                                          "max_date":max_date,"user_dates":user_dates,"user_datas":user_datas,"other_dates":other_dates,
                                          "other_datas":other_datas,"call_Agents":call_Agents,"third_dates":third_dates,"third_datas":third_datas,
                                          "start_date":start_date,"end_date":end_date,"current_kpi":current_kpi,"user_title": user_title,
                                          "other_title":other_title,"third_title":third_title,"permitted":permitted}) 



