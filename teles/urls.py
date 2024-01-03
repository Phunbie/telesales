from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home2'),
    path('home', views.home, name='home'),  
    path('profile/', views.profile, name='profile'),
    path('editprofile/', views.editProfile, name='editprofile'),
]

