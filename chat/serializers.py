# chat/serializers.py
from rest_framework import serializers
from .models import Thread, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    class Meta: model = Message; fields = ('id','sender','sender_name','text','image','created_at')

class ThreadSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta: model = Thread; fields = ('id','users','updated_at','messages')
