# chat/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer

class ThreadViewSet(viewsets.ModelViewSet):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(users=self.request.user).prefetch_related('messages')

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        t = self.get_object()
        msg = Message.objects.create(
            thread=t, sender=request.user,
            text=request.data.get('text',''), image=request.data.get('image',None)
        )
        return Response(MessageSerializer(msg).data)
