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


def percentage_grader(score):
    star = 1
    if score > 80:
        star = 5
    elif score > 60:
        star = 4
    elif score > 40:
        star = 3
    elif score > 20:
        star = 2
    else:
        star = 1
    return star


def general_average_grader(first,second,third):
    if first>100:
        first = 100
    if second>100:
        second = 100
    if third>100:
        third = 100
    avg = (first + second +third)/3
    avg = percentage_grader(avg)
    return avg
       
def goodbad(scale): 
    res = "Bad"
    if scale >= 3:
         res = "Good"
    return res

def scale_rating(scale):
    rating = "Do not meet expectation"
    if scale == 5:
        rating = "Outstanding"
    elif scale == 4:
        rating = "Exceeds expectations"   
    elif scale == 3:
        rating = "Meet Expectation"
    elif scale == 2:
        rating = "Partial meet expectation"
    elif scale == 1:
        rating = "Do not meet expectation"
    return rating

def star_grade(num):
    star_list = ["","","","",""]
    for i in range(num):
        star_list[i]= "checked"
    return star_list


def mergedf(collectiondf,negotiationdf,callsdf):
    df_merged = collectiondf.merge(callsdf, on=['User Name', 'Call Date', 'Country']).merge(negotiationdf, on=['User Name', 'Call Date', 'Country'])
    return df_merged 

def create_score_df(callskpi,collectionkpi,Negotiationkpi,df):
    df['score'] = ((df['Count Calls Connected'].str.replace(',', '').astype(int) * 100)/callskpi) + ((df['Negotiation Rate'].str.replace('%', '').astype(float) * 100)/Negotiationkpi) + ((df['Sum Total Paid'].str.replace(',', '').astype(float) *100)/collectionkpi)
    #final = df.groupby('User Name')['score'].sum().reset_index().sort_values(by='score')
    return df


def position_list(df):
    final = df.groupby('User Name')['score'].sum().reset_index().sort_values(by='score')
    return final['User Name'].tolist()



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
    agent_name = ""
    date_range = "MTD"
    agent_country = ""
    if request.method == 'POST':
        if request.POST.get('compare'):
            agent_name = request.POST.get('compare')
            date_range = request.POST.get('date-range2')
            agent_country = request.POST.get('country2')
        if request.POST.get('date-range'):
            date_range = request.POST.get('date-range')
        

    user = request.user
    agent= Agent.objects.get(user=user)
    username = request.user.username
    username = username.capitalize()
    first_name = agent.first_name
    last_name =  agent.last_name
    country = agent.country
    if agent_country:
        country = agent_country

    calls_target_daily = ""
    collection_target_daily  = ""
    Negotiation_target_daily  = ""
    #calls_target_monthly = ""
    #collection_target_monthly = ""
    #Negotiation_target_monthly = ""
    #calls_target_weekly = ""
    #collection_target_weekly  = ""
    #Negotiation_target_weekly  = ""
    if country == "Kenya":
        calls_target_daily = 200
        collection_target_daily  = 15833
        Negotiation_target_daily  = 60
        #calls_target_monthly = 4800
        #collection_target_monthly = 380000
        #Negotiation_target_monthly = 60
        #calls_target_weekly = 1200
        #collection_target_weekly  = 94998
        #Negotiation_target_weekly  = 60
    elif country == "Nigeria":
        calls_target_daily = 180
        collection_target_daily  = 145833
        Negotiation_target_daily  = 50
        #calls_target_monthly = 4320
        #collection_target_monthly = 3500000
        #Negotiation_target_monthly = 50
        #calls_target_weekly = 1080
        #collection_target_weekly  = 874998
        #Negotiation_target_weekly  = 50
    elif country == "Togo":
        calls_target_daily = 150
        collection_target_daily  = 104167
        Negotiation_target_daily  = 50
        #calls_target_monthly = 3600
        #collection_target_monthly =  2500000
        #Negotiation_target_monthly = 50
        #calls_target_weekly = 900
        #collection_target_weekly  = 625000
        #Negotiation_target_weekly  = 50
    elif country == "Uganda":
        calls_target_daily = 160
        collection_target_daily  = 500000
        Negotiation_target_daily  = 60
        #calls_target_monthly = 3840
        #collection_target_monthly = 12000000
        #Negotiation_target_monthly = 60
       #calls_target_weekly = 960
        #collection_target_weekly  = 3000000
        #Negotiation_target_weekly  = 60
    elif country == "Tanzania":
        calls_target_daily = 160
        collection_target_daily  = 325000
        Negotiation_target_daily  = 60
        #calls_target_monthly = 3840
        #collection_target_monthly = 7800000
        #Negotiation_target_monthly = 60
        #calls_target_weekly = 960
        #collection_target_weekly  = 1950000
       # Negotiation_target_weekly  = 60
    else:
        calls_target_daily = 200
        collection_target_daily  = 500000
        Negotiation_target_daily  = 65
       # calls_target_monthly = 4800
       # collection_target_monthly = 12000000
       # Negotiation_target_monthly = 65
       # calls_target_weekly = 1200
        #collection_target_weekly  = 3000000
       # Negotiation_target_weekly  = 65





    
    collection = bucket3('amount-collected-per-agent-mtd/')
    collection = collection.sort_values(by='Call Date')
    calls = bucket3('calls-per-agent-mtd/')
    calls = calls.sort_values(by='Call Date')
    contact_rate = bucket3('contact-rate-per-agent-mtd/')
    contact_rate = contact_rate.sort_values(by='Call Date')
    Negotiation = bucket3('negotiation-rate-individual-mtd/')
    Negotiation = Negotiation.sort_values(by='Call Date')
    user_list= collection['User Name'].unique().tolist()
    country_list = collection['Country'].unique().tolist()
    country_list = [i for i in country_list if i is not None]

    if date_range == "WTD":
        collection = bucket3('amount-collected-per-agent/')
        collection = collection.sort_values(by='Call Date')
        calls = bucket3('calls-per-agent/')
        calls = calls.sort_values(by='Call Date')
        contact_rate = bucket3('contact-rate-per-agent/')
        contact_rate = contact_rate.sort_values(by='Call Date')
        Negotiation = bucket3('negotiation-rate-individual/')
        Negotiation = Negotiation.sort_values(by='Call Date')
        user_list= collection['User Name'].unique().tolist()
        country_list = collection['Country'].unique().tolist()
        country_list = [i for i in country_list if i is not None]

    user_name = first_name.strip() + " " + last_name.strip()
    merged_kpi_df = mergedf(collection,Negotiation,calls)
    merged_kpi_df_scored = create_score_df(calls_target_daily,calls_target_daily, Negotiation_target_daily, merged_kpi_df)
    country_daf = ""
    if country in  country_list:
        country_daf = merged_kpi_df_scored[merged_kpi_df_scored['Country']==country]
    else:
        country_daf = merged_kpi_df_scored
    country_position_list = position_list(country_daf)
    country_agents_number = len(country_position_list)
    country_position_list.reverse()
    if  user_name in user_list:
        user_position = country_position_list.index(user_name) + 1
    else:
         user_position = "None"

    #print("agentpos", user_position,"number of agents",country_agents_number)

    #user_name = first_name.strip() + " " + last_name.strip()
    #defaults = len(calls["Call Date"].unique().tolist())
    #defaults = [ 0 for j in range(defaults)]
    #user_name = "Mercy Atieno"
    #user_name = "Adeola Adebayo"
    if  (user_name in user_list) or (agent_name in user_list):
        if agent_name in user_list:
            user_name = agent_name.strip()
        #user_name = "Peniel Ezechukwu"
        dates= calls[calls["User Name"] == user_name]["Call Date"].str.replace('-', '.')
        collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
        #print()
        total_paid_sum = collection[collection["User Name"] == user_name]["Sum Total Paid"].astype(float).tolist()    
        total_paid_sum = [round(num, 2) for num in total_paid_sum]
        #print(user_name)

        total_paid_kpi_percent = sum([i/collection_target_daily for i in total_paid_sum ])/len(total_paid_sum) * 100
        calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
        total_calls = calls[calls["User Name"] == user_name]["Count Calls Connected"].astype(float).tolist()
        total_calls = [round(num, 2) for num in total_calls]
        total_calls_kpi_percent = sum([i/calls_target_daily for i in total_calls])/len(total_calls) * 100
        #print("calls:",calls_target_daily)
        #print("calls2:",total_calls)
        #print(total_calls_kpi_percent)

        contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
        contact = contact_rate[contact_rate["User Name"] == user_name]["Contact Rate"].astype(float).tolist()
        contact = [round(num, 2) for num in contact]
        Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
        Negotiation_r = Negotiation[Negotiation["User Name"] == user_name]["Negotiation Rate"].astype(float).tolist()
        Negotiation_r = [round(num, 2) for num in  Negotiation_r]

        Negotiation_kpi_percent = sum([i/Negotiation_target_daily for i in Negotiation_r])/len(Negotiation_r) * 100
    elif (country in country_list) and (user_name not in user_list):
        dates= calls[calls["Country"] == country]["Call Date"].str.replace('-', '.')
        collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '').astype(int)
        total_paid_sum = collection[collection["Country"] == country]
        total_paid_sum = total_paid_sum.groupby('Call Date')['Sum Total Paid'].mean().reset_index()
        dates= total_paid_sum["Call Date"].str.replace('-', '.')
        total_paid_sum = total_paid_sum.sort_values(by='Call Date')
        total_paid_sum = total_paid_sum["Sum Total Paid"].tolist()
        total_paid_sum = [round(num, 2) for num in total_paid_sum]
        total_paid_kpi_percent = sum([i/collection_target_daily for i in total_paid_sum ])/len(total_paid_sum) * 100
# calls
        calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '').astype(int)
        total_calls = calls[calls["Country"] == country]
        total_calls = total_calls.groupby('Call Date')['Count Calls Connected'].mean().reset_index()
        total_calls= total_calls.sort_values(by='Call Date')
        total_calls = total_calls["Count Calls Connected"].tolist()
        total_calls = [round(num, 2) for num in total_calls]
        total_calls_kpi_percent = sum([i/calls_target_daily for i in total_calls])/len(total_calls) * 100
        #print("calls:",calls_target_daily)
        #print("calls2:",total_calls)
        #print(total_calls_kpi_percent)
# contact
        contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '').astype(float)
        contact  = contact_rate[contact_rate["Country"] == country]
        contact  =  contact.groupby('Call Date')['Contact Rate'].mean().reset_index()
        contact =  contact.sort_values(by='Call Date')
        contact  =  contact["Contact Rate"].tolist()
        contact = [round(num, 2) for num in contact]    
#Negotiation
        Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '').astype(float)
        Negotiation_r =  Negotiation[Negotiation["Country"] == country]
        Negotiation_r = Negotiation_r.groupby('Call Date')['Negotiation Rate'].mean().reset_index()
        Negotiation_r = Negotiation_r.sort_values(by='Call Date')
        Negotiation_r = Negotiation_r["Negotiation Rate"].tolist()
        Negotiation_r = [round(num, 2) for num in  Negotiation_r]
        Negotiation_kpi_percent = sum([i/Negotiation_target_daily for i in Negotiation_r])/len(Negotiation_r) * 100

        #collection_target_daily
        #calls_target_daily
       # Negotiation_target_daily
    else:
        country = "Nigeria"
        dates= calls[calls["Country"] == country]["Call Date"].str.replace('-', '.')
        collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '').astype(int)
        total_paid_sum = collection[collection["Country"] == country]
        total_paid_sum = total_paid_sum.groupby('Call Date')['Sum Total Paid'].mean().reset_index()
        dates= total_paid_sum["Call Date"].str.replace('-', '.')
        total_paid_sum = total_paid_sum.sort_values(by='Call Date')
        total_paid_sum = total_paid_sum["Sum Total Paid"].tolist()
        total_paid_sum = [round(num, 2) for num in total_paid_sum]
        total_paid_kpi_percent = sum([i/collection_target_daily for i in total_paid_sum ])/len(total_paid_sum) * 100
# calls
        calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '').astype(int)
        total_calls = calls[calls["Country"] == country]
        total_calls = total_calls.groupby('Call Date')['Count Calls Connected'].mean().reset_index()
        total_calls= total_calls.sort_values(by='Call Date')
        total_calls = total_calls["Count Calls Connected"].tolist()
        total_calls = [round(num, 2) for num in total_calls]
        total_calls_kpi_percent = sum([i/calls_target_daily for i in total_calls])/len(total_calls) * 100
# contact
        contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '').astype(float)
        contact  = contact_rate[contact_rate["Country"] == country]
        contact  =  contact.groupby('Call Date')['Contact Rate'].mean().reset_index()
        contact =  contact.sort_values(by='Call Date')
        contact  =  contact["Contact Rate"].tolist()
        contact = [round(num, 2) for num in contact]    
#Negotiation
        Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '').astype(float)
        Negotiation_r =  Negotiation[Negotiation["Country"] == country]
        Negotiation_r = Negotiation_r.groupby('Call Date')['Negotiation Rate'].mean().reset_index()
        Negotiation_r = Negotiation_r.sort_values(by='Call Date')
        Negotiation_r = Negotiation_r["Negotiation Rate"].tolist()
        Negotiation_r = [round(num, 2) for num in  Negotiation_r]
        Negotiation_kpi_percent = sum([i/Negotiation_target_daily for i in Negotiation_r])/len(Negotiation_r) * 100



   #grading

   #percentage_grader(score) total_paid_kpi_percent total_calls_kpi_percent  Negotiation_kpi_percent  kpi_grade Kpi_percent  scale_rating(scale):
    total_paid_kpi_grade = percentage_grader(total_paid_kpi_percent)
    total_calla_kpi_grade = percentage_grader(total_calls_kpi_percent)
    Negotiation_kpi_grade = percentage_grader(Negotiation_kpi_percent) 

    total_paid_scale_rating = scale_rating( total_paid_kpi_grade)
    total_calla_scale_rating = scale_rating(total_calla_kpi_grade)
    Negotiation_scale_rating = scale_rating(Negotiation_kpi_grade)

    total_paid_scale_status = goodbad(total_paid_kpi_grade)
    total_calla_scale_status = goodbad(total_calla_kpi_grade)
    Negotiation_scale_status = goodbad(Negotiation_kpi_grade)


    general_score_percent = (total_paid_kpi_percent + total_calls_kpi_percent + Negotiation_kpi_percent)/3
    #print("general:",general_score_percent,total_paid_kpi_percent,total_calls_kpi_percent,Negotiation_kpi_percent)
    
    #general_score_grade = percentage_grader(general_score_percent)
    general_score_grade = general_average_grader(total_paid_kpi_percent, total_calls_kpi_percent, Negotiation_kpi_percent)
    general_rating = scale_rating(general_score_grade)
    stars = star_grade(general_score_grade)
    general_status = goodbad(general_score_grade)



    kpi_grade = {"total_paid_kpi_grade":total_paid_kpi_grade,"total_calla_kpi_grade":total_calla_kpi_grade, "Negotiation_kpi_grade": Negotiation_kpi_grade }
    Kpi_percent = {"total_paid_kpi_percent":total_paid_kpi_percent,"total_calls_kpi_percent":total_calls_kpi_percent,"Negotiation_kpi_percent":Negotiation_kpi_percent}
    kpi_scale_rating = {"total_paid_scale_rating":total_paid_scale_rating,"total_calla_scale_rating": total_calla_scale_rating,"Negotiation_scale_rating":Negotiation_scale_rating }

    collection_bar_color = [int(x>=collection_target_daily) for x in total_paid_sum]
    collection_daily_target_list = [collection_target_daily for x in total_paid_sum]
    length_paid = len(total_paid_sum) -1
    latest_paid = total_paid_sum[length_paid]
    #print(f"The sum total paid for {user_name} is: {total_paid_sum}")
    #calls
   # calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
   # total_calls = calls[calls["User Name"] == user_name]["Count Calls Connected"].astype(int).tolist()
    call_bar_color = [int(x>=calls_target_daily) for x in total_calls]
    call_daily_target_list = [calls_target_daily for x in total_calls]

    #dates= calls[calls["User Name"] == user_name]["Call Date"].str.replace('-', '.')      .astype(float)
    dash_date = dates.str[5:].tolist()
    dash_date = json.dumps(dash_date)
    #print(dash_date)
    length_call = len(total_calls) -1
    latest_call = total_calls[length_call]
    #contact_rate
   # contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
   # contact = contact_rate[contact_rate["User Name"] == user_name]["Contact Rate"].astype(float).tolist()
    length_contact = len(contact) - 1
    latest_contact = contact[length_contact]
    #contact = round(contact, 2)
    #Negotiation
  #  Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
   # Negotiation_r = Negotiation[Negotiation["User Name"] == user_name]["Negotiation Rate"].astype(float).tolist()
    Negotiation_bar_color =  [int(x>=Negotiation_target_daily) for x in Negotiation_r]
    Negotiation_daily_target_list = [Negotiation_target_daily for x in Negotiation_r]
    length_negotiotion = len(Negotiation_r) - 1
    #print(f"Negotiation_r: {Negotiation_r}")
    latest_negotiation = Negotiation_r[length_negotiotion]
    #latest_negotiation = Negotiation_r[-1]
    bar_colors = {"calls":call_bar_color,"collection":collection_bar_color,"Negotiation":Negotiation_bar_color}
    daily_targets = {"calls":call_daily_target_list,"collection":collection_daily_target_list,"Negotiation": Negotiation_daily_target_list}
    #Negotiation_r = round(Negotiation_r, 2)
    input_list = {"total_paid_sum":total_paid_sum,
                   "total_calls":total_calls,
                   "contact":contact,
                   "Negotiation":Negotiation_r,"latest_paid":latest_paid,
                   "latest_call":latest_call,
                   "latest_contact":latest_contact,
                   "latest_negotiation":latest_negotiation,
                     "first_name":first_name,
                       "last_name":last_name,
                       "dash_date":dash_date,
                       "bar_colors":bar_colors,
                       "daily_targets": daily_targets,
                       "country":country,
                       "total_paid_scale_status":total_paid_scale_status,
                       "total_calla_scale_status":total_calla_scale_status,
                       "Negotiation_scale_status":Negotiation_scale_status,
                       "general_status": general_status,
                       "agent_name": agent_name,
                       "user_is_supervisor": request.user.groups.filter(name="Supervisor").exists()
                       }
    name_list = user_list
    user_list = json.dumps(user_list)
    return render(request, 'monitor.html', {'username': username,'agent':agent,"input_list":input_list,
                                             "user_list": user_list,"kpi_grade":kpi_grade,"Kpi_percent" :Kpi_percent,
                                             "kpi_scale_rating":kpi_scale_rating, "name_list":name_list,"date_range":date_range,
                                             "general_score_percent":general_score_percent,"general_score_grade":general_score_grade,
                                             "stars":stars,"general_rating":general_rating,"user_position":user_position,"country_agents_number":country_agents_number})


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