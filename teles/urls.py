from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home2'),
    path('home', views.home, name='home'),
    path('signup/', views.signUp, name='signup'),
    path('login/', views.logIn, name='login'),
    path('signout/', views.signOut, name='signout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('editprofile/', views.editProfile, name='editprofile'),
    path('dataapi/', views.dataapi, name='dataapi'),
    path('callsapi/', views.callsapi, name='callsapi'),
    path('agentlist/', views.agentlist, name='agentlist'),
    path ('agent_info/<str:id>/', views.agent_info, name='agent_info'),
    path ('monitor/', views.monitor, name='monitor'),
]

