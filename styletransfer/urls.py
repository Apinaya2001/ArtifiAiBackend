from django.urls import path
from .views import style_transfer_view

urlpatterns = [
    path('style-transfer/', style_transfer_view),
]
