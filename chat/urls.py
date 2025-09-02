# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.start_conversation),
    path("conversations/", views.conversation_list),
    path("conversations/<int:pk>/messages/", views.conversation_messages),
    path("conversations/<int:pk>/read/", views.mark_read),
]
