from django.urls import path
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from . import views

me_view        = permission_classes([IsAuthenticated])(views.me)
logout_view    = permission_classes([IsAuthenticated])(views.logout)
change_pw_view = permission_classes([IsAuthenticated])(views.change_password)

urlpatterns = [
    path("register/", views.register),
    path("login/", views.login),
    path("refresh/", views.refresh),         # <-- add this
    path("me/", me_view),
    path("change-password/", change_pw_view),
    path("logout/", logout_view),
]
