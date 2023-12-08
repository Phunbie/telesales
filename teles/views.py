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


def up_down_indicator(list):
    res= "fa-stop"
    if len(list) > 1:
        increase = list[-1] - list[-2]
        if increase > 0:
            res = "fa-caret-up"
        elif increase < 0:
            res = "fa-caret-down"
        else:
            res= "fa-stop"
    return res



Kenya_calls_target_daily = 200
Kenya_collection_target_daily  = 15833
Kenya_Negotiation_target_daily  = 60
Kenya_calls_target_monthly = 4800
Kenya_collection_target_monthly = 380000
Kenya_Negotiation_target_monthly = 60
Kenya_calls_target_weekly = 1200
Kenya_collection_target_weekly  = 94998
Kenya_Negotiation_target_weekly  = 60
Nigeria_calls_target_daily = 180
Nigeria_collection_target_daily  = 145833
Nigeria_Negotiation_target_daily  = 50
Nigeria_calls_target_monthly = 4320
Nigeria_collection_target_monthly = 3500000
Nigeria_Negotiation_target_monthly = 50
Nigeria_calls_target_weekly = 1080
Nigeria_collection_target_weekly  = 874998
Nigeria_Negotiation_target_weekly  = 50
Togo_calls_target_daily = 150
Togo_collection_target_daily  = 104167
Togo_Negotiation_target_daily  = 50
Togo_calls_target_monthly = 3600
Togo_collection_target_monthly =  2500000
Togo_Negotiation_target_monthly = 50
Togo_calls_target_weekly = 900
Togo_collection_target_weekly  = 625000
Togo_Negotiation_target_weekly  = 50
Uganda_calls_target_daily = 160
Uganda_collection_target_daily  = 500000
Uganda_Negotiation_target_daily  = 60
Uganda_calls_target_monthly = 3840
Uganda_collection_target_monthly = 12000000
Uganda_Negotiation_target_monthly = 60
Uganda_calls_target_weekly = 960
Uganda_collection_target_weekly  = 3000000
Uganda_Negotiation_target_weekly  = 60
Tanzania_calls_target_daily = 160
Tanzania_collection_target_daily  = 325000
Tanzania_Negotiation_target_daily  = 60
Tanzania_calls_target_monthly = 3840
Tanzania_collection_target_monthly = 7800000
Tanzania_Negotiation_target_monthly = 60
Tanzania_calls_target_weekly = 960
Tanzania_collection_target_weekly  = 1950000
Tanzania_Negotiation_target_weekly  = 60


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




def home(request):
    #post conditional filter list by country
    scan_country=""
    date_range = "MTD"
    if request.method == 'POST':
        scan_country  = request.POST.get('country')
        date_range = request.POST.get('date-range')
        redirect(home)

        
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
        country = agent.country
        #daily, weekly & monthly kpi target per country
        calls_target_daily = ""
        collection_target_daily  = ""
        Negotiation_target_daily  = ""
        calls_target_monthly = ""
        collection_target_monthly = ""
        Negotiation_target_monthly = ""
        calls_target_weekly = ""
        collection_target_weekly  = ""
        Negotiation_target_weekly  = ""
        if country == "Kenya":
            calls_target_daily = 200
            collection_target_daily  = 15833
            Negotiation_target_daily  = 60
            calls_target_monthly = 4800
            collection_target_monthly = 380000
            Negotiation_target_monthly = 60
            calls_target_weekly = 1200
            collection_target_weekly  = 94998
            Negotiation_target_weekly  = 60
        elif country == "Nigeria":
            calls_target_daily = 180
            collection_target_daily  = 145833
            Negotiation_target_daily  = 50
            calls_target_monthly = 4320
            collection_target_monthly = 3500000
            Negotiation_target_monthly = 50
            calls_target_weekly = 1080
            collection_target_weekly  = 874998
            Negotiation_target_weekly  = 50
        elif country == "Togo":
            calls_target_daily = 150
            collection_target_daily  = 104167
            Negotiation_target_daily  = 50
            calls_target_monthly = 3600
            collection_target_monthly =  2500000
            Negotiation_target_monthly = 50
            calls_target_weekly = 900
            collection_target_weekly  = 625000
            Negotiation_target_weekly  = 50
        elif country == "Uganda":
            calls_target_daily = 160
            collection_target_daily  = 500000
            Negotiation_target_daily  = 60
            calls_target_monthly = 3840
            collection_target_monthly = 12000000
            Negotiation_target_monthly = 60
            calls_target_weekly = 960
            collection_target_weekly  = 3000000
            Negotiation_target_weekly  = 60
        elif country == "Tanzania":
            calls_target_daily = 160
            collection_target_daily  = 325000
            Negotiation_target_daily  = 60
            calls_target_monthly = 3840
            collection_target_monthly = 7800000
            Negotiation_target_monthly = 60
            calls_target_weekly = 960
            collection_target_weekly  = 1950000
            Negotiation_target_weekly  = 60
        else:
            calls_target_daily = 200
            collection_target_daily  = 500000
            Negotiation_target_daily  = 65
            calls_target_monthly = 4800
            collection_target_monthly = 12000000
            Negotiation_target_monthly = 65
            calls_target_weekly = 1200
            collection_target_weekly  = 3000000
            Negotiation_target_weekly  = 65

        collection = bucket3('amount-collected-per-agent-mtd/')
        collection = collection.sort_values(by='Call Date')
        calls = bucket3('calls-per-agent-mtd/')
        calls = calls.sort_values(by='Call Date')
        contact_rate = bucket3('contact-rate-per-agent-mtd/')
        contact_rate = contact_rate.sort_values(by='Call Date')
        Negotiation = bucket3('negotiation-rate-individual-mtd/')
        Negotiation = Negotiation.sort_values(by='Call Date')

        if date_range == "WTD":
            collection = bucket3('amount-collected-per-agent/')
            collection = collection.sort_values(by='Call Date')
            calls = bucket3('calls-per-agent/')
            calls = calls.sort_values(by='Call Date')
            contact_rate = bucket3('contact-rate-per-agent/')
            contact_rate = contact_rate.sort_values(by='Call Date')
            Negotiation = bucket3('negotiation-rate-individual/')
            Negotiation = Negotiation.sort_values(by='Call Date')
    
   

       

        #create a position list
        #original dataframes
        merged_df =  mergedf(collection, Negotiation, calls)


   

        # dataframe per country score added
        Nigeria_df = merged_df[merged_df['Country']=="Nigeria"]
        Nigeria_df_scored = create_score_df(Nigeria_calls_target_daily, Nigeria_collection_target_daily,Nigeria_Negotiation_target_daily, Nigeria_df)
        Nigeria_first = position_list(Nigeria_df_scored)[-1]
        Kenya_df = merged_df[merged_df['Country']=="Kenya"]
        Kenya_df_scored = create_score_df(Kenya_calls_target_daily, Kenya_collection_target_daily,Kenya_Negotiation_target_daily,  Kenya_df)
        Kenya_first = position_list(Kenya_df_scored)[-1]
        Tanzania_df = merged_df[merged_df['Country']=="Tanzania"]
        Tanzania_df_scored = create_score_df( Tanzania_calls_target_daily, Tanzania_collection_target_daily, Tanzania_Negotiation_target_daily, Tanzania_df)
        Tanzania_first = position_list(Tanzania_df_scored)[-1]
        Uganda_df = merged_df[merged_df['Country']=="Uganda"] 
        Uganda_df_scored = create_score_df(Uganda_calls_target_daily, Uganda_collection_target_daily,Uganda_Negotiation_target_daily, Uganda_df ) 
        Uganda_first = position_list(Uganda_df_scored)[-1]
        #append all the scored country's dfs 
        scored_joined = pd.concat([Nigeria_df_scored, Kenya_df_scored, Tanzania_df_scored, Uganda_df_scored ], axis=0)
        dfscore=""
        checker=False
        if scan_country == "Nigeria":
            dfscore = Nigeria_df_scored
            checker=True
        elif scan_country == "Kenya":
            dfscore = Kenya_df_scored
            checker=True
        elif scan_country == "Tanzania":
            dfscore = Tanzania_df_scored
            checker=True
        elif scan_country == "Uganda":
            dfscore = Uganda_df_scored
            checker=True
        else:
            pass
        #return redirect('home',test_country)

        first_in_country = {"Nigeria":Nigeria_first,"Kenya":Kenya_first, "Tanzania":Tanzania_first,"Uganda":Uganda_first}
       

        if checker:
            user_list = position_list(dfscore)
        else:
            user_list = position_list(scored_joined)

        user_list= user_list[::-1]

        user_list2 = position_list(scored_joined)
        combined_list = ""
        list_name = []
        list_collection =[]
        list_call = []
        list_contact = []
        list_negotiation =[]
        for i, user_name in enumerate(user_list):
            collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
            total_paid_sum = collection[collection["User Name"] == user_name]["Sum Total Paid"].astype(float).sum()
            total_paid_sum = round(total_paid_sum,2)
            #calls
            calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
            total_calls = calls[calls["User Name"] == user_name]["Count Calls Connected"].astype(float).sum()
            total_calls = round(total_calls,2)
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
        country_list = collection['Country'].unique().tolist()
        country_list = [i for i in country_list if i is not None]
        
        user_name = first_name.strip() + " " + last_name.strip() 
        
        if  user_name in user_list2:
            #user_name = "Peniel Ezechukwu"
            collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
            total_paid_sum = collection[collection["User Name"] == user_name]["Sum Total Paid"].astype(float).tolist()
            total_paid_sum = [round(num, 2) for num in total_paid_sum]
            calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
            total_calls = calls[calls["User Name"] == user_name]["Count Calls Connected"].astype(float).tolist()
            total_calls = [round(num, 2) for num in  total_calls]
            contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
            contact = contact_rate[contact_rate["User Name"] == user_name]["Contact Rate"].astype(float).tolist()
            contact = [round(num, 2) for num in contact]
            Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
            Negotiation_r = Negotiation[Negotiation["User Name"] == user_name]["Negotiation Rate"].astype(float).tolist()
            Negotiation_r = [round(num, 2) for num in Negotiation_r]

            print("total_paid_sum",total_paid_sum)
        elif (country in country_list) and (user_name not in user_list2):
            collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '').astype(int)
            total_paid_sum = collection[collection["Country"] == country]
            total_paid_sum = total_paid_sum.groupby('Call Date')['Sum Total Paid'].mean().reset_index()
            #dates= total_paid_sum["Call Date"].str.replace('-', '.')
            total_paid_sum = total_paid_sum.sort_values(by='Call Date')
            total_paid_sum = total_paid_sum["Sum Total Paid"].tolist()
            total_paid_sum = [round(num, 2) for num in total_paid_sum]
    # calls
            calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '').astype(int)
            total_calls = calls[calls["Country"] == country]
            total_calls = total_calls.groupby('Call Date')['Count Calls Connected'].mean().reset_index()
            total_calls= total_calls.sort_values(by='Call Date')
            total_calls = total_calls["Count Calls Connected"].tolist()
            total_calls = [round(num, 2) for num in  total_calls]
            #calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
            #total_calls = calls[calls["Country"] == country]["Count Calls Connected"].astype(int).tolist()
    # contact
            contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '').astype(float)
            contact  = contact_rate[contact_rate["Country"] == country]
            contact  =  contact.groupby('Call Date')['Contact Rate'].mean().reset_index()
            contact =  contact.sort_values(by='Call Date')
            contact  =  contact["Contact Rate"].tolist()
            contact = [round(num, 2) for num in contact]
        # contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
        # contact = contact_rate[contact_rate["Country"] == country]["Contact Rate"].astype(float).tolist()
    #Negotiation
            Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '').astype(float)
            Negotiation_r =  Negotiation[Negotiation["Country"] == country]
            Negotiation_r = Negotiation_r.groupby('Call Date')['Negotiation Rate'].mean().reset_index()
            Negotiation_r = Negotiation_r.sort_values(by='Call Date')
            Negotiation_r = Negotiation_r["Negotiation Rate"].tolist()
            Negotiation_r = [round(num, 2) for num in Negotiation_r]
            print("total_paid_sum2",total_paid_sum)   
           # collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
            #total_paid_sum = collection[collection["Country"] == country]["Sum Total Paid"].astype(int).tolist()
           # calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
           # total_calls = calls[calls["Country"] == country]["Count Calls Connected"].astype(int).tolist()
           # contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
           # contact = contact_rate[contact_rate["Country"] == country]["Contact Rate"].astype(float).tolist()
           # Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
           # Negotiation_r = Negotiation[Negotiation["Country"] == country]["Negotiation Rate"].astype(float).tolist()
        else:
            country = "Nigeria"
            collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '').astype(int)
            total_paid_sum = collection[collection["Country"] == country]
            total_paid_sum = total_paid_sum.groupby('Call Date')['Sum Total Paid'].mean().reset_index()
            #dates= total_paid_sum["Call Date"].str.replace('-', '.')
            total_paid_sum = total_paid_sum.sort_values(by='Call Date')
            total_paid_sum = total_paid_sum["Sum Total Paid"].tolist()
            total_paid_sum = [round(num, 2) for num in total_paid_sum]
    # calls
            calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '').astype(int)
            total_calls = calls[calls["Country"] == country]
            total_calls = total_calls.groupby('Call Date')['Count Calls Connected'].mean().reset_index()
            total_calls= total_calls.sort_values(by='Call Date')
            total_calls = total_calls["Count Calls Connected"].tolist()
            total_calls = [round(num, 2) for num in  total_calls]
            #calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
            #total_calls = calls[calls["Country"] == country]["Count Calls Connected"].astype(int).tolist()
    # contact
            contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '').astype(float)
            contact  = contact_rate[contact_rate["Country"] == country]
            contact  =  contact.groupby('Call Date')['Contact Rate'].mean().reset_index()
            contact =  contact.sort_values(by='Call Date')
            contact  =  contact["Contact Rate"].tolist()
            contact = [round(num, 2) for num in contact]
        # contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
        # contact = contact_rate[contact_rate["Country"] == country]["Contact Rate"].astype(float).tolist()
    #Negotiation
            Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '').astype(float)
            Negotiation_r =  Negotiation[Negotiation["Country"] == country]
            Negotiation_r = Negotiation_r.groupby('Call Date')['Negotiation Rate'].mean().reset_index()
            Negotiation_r = Negotiation_r.sort_values(by='Call Date')
            Negotiation_r = Negotiation_r["Negotiation Rate"].tolist()
            Negotiation_r = [round(num, 2) for num in Negotiation_r]
           


            #user_name = "Adeola Adebayo"
        #collection
       # collection["Sum Total Paid"] = collection["Sum Total Paid"].str.replace(',', '')
       # total_paid_sum = collection[collection["User Name"] == user_name]["Sum Total Paid"].astype(int).tolist()
        collection_increase = up_down_indicator(total_paid_sum)
        
        total_paid_sum = total_paid_sum[-1]
        #print(f"The sum total paid for {user_name} is: {total_paid_sum}")
        #calls
       # calls["Count Calls Connected"] = calls["Count Calls Connected"].str.replace(',', '')
       # total_calls = calls[calls["User Name"] == user_name]["Count Calls Connected"].astype(int).tolist()
        calls_increase = up_down_indicator(total_calls)
        total_calls = total_calls[-1]
        #contact_rate
       # contact_rate["Contact Rate"] = contact_rate["Contact Rate"].str.replace('%', '')
       # contact = contact_rate[contact_rate["User Name"] == user_name]["Contact Rate"].astype(float).tolist()
        contact_increase = up_down_indicator(contact)
        contact = contact[-1]
        #length = len(contact)
        #contact=contact.sum()/length 
        contact = round(contact, 2)
        #Negotiation
       # Negotiation["Negotiation Rate"] = Negotiation["Negotiation Rate"].str.replace('%', '')
       # Negotiation_r = Negotiation[Negotiation["User Name"] == user_name]["Negotiation Rate"].astype(float).tolist()
        Negotiation_increase = up_down_indicator(Negotiation_r)
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
                   "combined_list": combined_list,
                   "first_in_country":first_in_country,
                   "kpi_increment_list": kpi_increment_list,
                   "scan_country":scan_country,
                   }
        
        return render(request, 'index.html',context )
    return redirect(logIn) 

def leaderboard(request):

     #kpi goals
    callskpi = 200
    collectionkpi = 400000
    negotiationkpi = 60


    collection = bucket3('amount-collected-per-agent/')
    collection = collection.sort_values(by='Call Date')
    calls = bucket3('calls-per-agent/')
    calls = calls.sort_values(by='Call Date')
    contact_rate = bucket3('contact-rate-per-agent/')
    contact_rate = contact_rate.sort_values(by='Call Date')
    Negotiation = bucket3('negotiation-rate-individual/')
    Negotiation = Negotiation.sort_values(by='Call Date')

     #create a position list
    merged_df =  mergedf(collection, Negotiation, calls)



     # dataframe per country score added
    Nigeria_df = merged_df[merged_df['Country']=="Nigeria"]
    Nigeria_df_scored = create_score_df(Nigeria_calls_target_daily, Nigeria_collection_target_daily,Nigeria_Negotiation_target_daily, Nigeria_df)
    Kenya_df = merged_df[merged_df['Country']=="Kenya"]
    Kenya_df_scored = create_score_df(Kenya_calls_target_daily, Kenya_collection_target_daily,Kenya_Negotiation_target_daily,  Kenya_df)
    Tanzania_df = merged_df[merged_df['Country']=="Tanzania"]
    Tanzania_df_scored = create_score_df( Tanzania_calls_target_daily, Tanzania_collection_target_daily, Tanzania_Negotiation_target_daily, Tanzania_df)
    Uganda_df = merged_df[merged_df['Country']=="Uganda"] 
    Uganda_df_scored = create_score_df(Uganda_calls_target_daily, Uganda_collection_target_daily,Uganda_Negotiation_target_daily, Uganda_df ) 

    #append all the scored country's dfs 
    scored_joined = pd.concat([Nigeria_df_scored, Kenya_df_scored, Tanzania_df_scored, Uganda_df_scored ], axis=0)



    user_list = position_list(scored_joined)

    user_list= user_list[::-1]



    #user_list= collection['User Name'].unique().tolist()


    combined_list = ""
    list_name = []
    list_collection =[]
    list_call = []
    list_contact = []
    list_negotiation =[]
    for  user_name in user_list:
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
        combined_list = list(zip(list_name, list_collection, list_call, list_contact, list_negotiation))
       
        context = {
                   "combined_list": combined_list
                   }
        

    return render(request, 'leaderboard.html',context )



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
