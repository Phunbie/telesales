from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from teles.models import Agent
from .models import Feedback, Vote, Comment
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse



def dashview(request):
    user= request.user
    username = user.username
    if request.method == 'POST':
        message = request.POST.get('message')
        feedback = Feedback(
            user=user,
            text= message,
        )
        feedback.save()
        vote = Vote(user=user,feedback=feedback, value=False)
        vote.save()
    votes = Vote.objects.all().order_by('-feedback_id') #.values()

    return render(request, 'dashview.html',{'username':username,'votes':votes})

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
        

    