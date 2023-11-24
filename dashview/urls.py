from django.urls import path
from . import views

urlpatterns = [
     path('', views.dashview, name='dashview'),
     path ('upvote/<str:uid>/', views.upvote, name='upvote'),
]