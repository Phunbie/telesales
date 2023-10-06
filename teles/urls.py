from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home2'),
    path('home', views.home, name='home'),
    path('signup/', views.signUp, name='signup'),
    path('login/', views.logIn, name='login'),
    path('signout/', views.signOut, name='signout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]