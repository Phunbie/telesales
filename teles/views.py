from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from .models import Agent
from authentication.views import logIn
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import vicidata


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
        return render(request, 'index.html', {'username': username,'email':email,'agent':agent,'angaza_id':angaza_id,'country':country,'role':role})
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


    return render(request, 'editprof.html', {'username': username,'email':email,'angaza_id':angaza_id,'country':country,'role':role})



def password(request):
    return render(request, 'password.html')
