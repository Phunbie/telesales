from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signUp, name='signup'),
    path('login/', views.logIn, name='login'),
    path('signout/', views.signOut, name='signout'),
]