# # accounts/views.py
# from django.contrib.auth.models import User
# from rest_framework import generics, permissions
# from rest_framework.response import Response

# class RegisterView(generics.CreateAPIView):
#     permission_classes = [permissions.AllowAny]
#     def post(self, request):
#         u = User.objects.create_user(
#             username=request.data['username'],
#             email=request.data.get('email',''),
#             password=request.data['password']
#         )
#         return Response({'id': u.id, 'username': u.username})

# class MeView(generics.RetrieveAPIView):
#     def get(self, request):
#         u = request.user
#         return Response({'id': u.id, 'username': u.username, 'email': u.email})
# accounts/views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken


def _tokens_for_user(user: User):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email", "")
        password = request.data.get("password")

        if not username or not password:
            return Response({"detail": "username and password required"}, status=400)

        try:
            u = User.objects.create_user(username=username, email=email, password=password)
        except IntegrityError:
            return Response({"detail": "username already exists"}, status=400)

        access, refresh = _tokens_for_user(u)
        return Response(
            {
                "access": access,
                "refresh": refresh,
                "user": {
                    "id": u.id,
                    "username": u.username,
                    "name": u.get_full_name() or u.username,
                    "email": u.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([AllowAny])  # public
def login_view(request):
    ident = request.data.get("username") or request.data.get("email")
    password = request.data.get("password")
    if not ident or not password:
        return Response({"detail": "username/email and password required"}, status=400)

    # Allow email login by resolving to username if email was provided
    username = ident
    if "@" in ident:
        try:
            username = User.objects.get(email__iexact=ident).username
        except User.DoesNotExist:
            pass

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=401)

    access, refresh = _tokens_for_user(user)
    return Response(
        {
            "access": access,
            "refresh": refresh,
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.get_full_name() or user.username,
                "email": user.email,
            },
        }
    )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "name": u.get_full_name() or u.username,
            }
        )
