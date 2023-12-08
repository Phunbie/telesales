
from django.db import models
from django.contrib.auth.models import User

#class Feedback(models.Model):
  #text = models.TextField()
  #user = models.ForeignKey(User, on_delete=models.CASCADE)
  #agent_name = models.TextField(default="name")
  #totalvote = models.IntegerField(default=0)
  #date = models.DateField(auto_now_add=True)


#class Vote(models.Model):
  # user = models.ForeignKey(User, on_delete=models.CASCADE)
  # feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE)
  # value = models.BooleanField() # True for upvote, False for downvote
   #class Meta:
    #  unique_together = ('user', 'feedback',)

class Feedbacknew(models.Model):
  text = models.TextField()
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  agent = models.TextField(default="name")
  date = models.DateField(auto_now_add=True)

class Comment(models.Model):
  text = models.TextField()
  feedback = models.ForeignKey(Feedbacknew, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  date = models.DateField(auto_now_add=True)


