from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from teles.models import Agent
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def report(request):
    username = request.user.username
    return render(request, 'report.html',{'username':username}) 