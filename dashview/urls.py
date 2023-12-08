from django.urls import path
from . import views

urlpatterns = [
     path('', views.dashview, name='dashview'),
     path('feedback_comment/<str:f_id>/', views.feedback_comment, name='replies'),
]