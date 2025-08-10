# chat/models.py
from django.db import models
from django.contrib.auth.models import User

class Thread(models.Model):
    users = models.ManyToManyField(User, related_name='threads')
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
