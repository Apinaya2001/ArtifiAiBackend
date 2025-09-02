# chat/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone

class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="chat_conversations"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

def upload_to(instance, filename):
    ts = timezone.now().strftime("%Y/%m")
    return f"chat/{instance.conversation_id}/{ts}/{filename}"

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        related_name="messages",           # ← IMPORTANT: “messages”
        on_delete=models.CASCADE,
        null=True, blank=True,
    )
    sender   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text     = models.TextField(blank=True)
    image    = models.ImageField(upload_to=upload_to, blank=True, null=True)
    created  = models.DateTimeField(auto_now_add=True)  # ← you already renamed
