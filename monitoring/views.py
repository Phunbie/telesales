from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from teles.models import Agent
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required



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
