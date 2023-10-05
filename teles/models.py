from django.db import models
#from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

"""
class User(AbstractUser):
    angaza_id = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
"""


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    angaza_id = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
