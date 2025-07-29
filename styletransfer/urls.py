# styletransfer/urls.py
from django.urls import path
from .views import style_transfer

urlpatterns = [
    path('style/transfer/', style_transfer),
]
