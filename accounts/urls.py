from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, me_user, ChangePasswordView

urlpatterns = [
    path("login/",   TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(),     name="token_refresh"),
    path("register/", RegisterView.as_view(),        name="register"),
    path("me/",       me_user,                       name="me_user"),
    path("password/", ChangePasswordView.as_view(),  name="change_password"),
]
    