from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistedToken, OutstandingToken

from .serializers import RegisterSerializer, UserSerializer

def _token_payload_for(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data,
    }

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        user = s.save()
        update_last_login(None, user)
        return Response(_token_payload_for(user), status=201)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error": "username and password required"}, status=400)

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        update_last_login(None, user)
        return Response(_token_payload_for(user), status=200)

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class LogoutView(APIView):
    """
    Blacklists the provided refresh token (requires token_blacklist app).
    Body: { "refresh": "<refresh_token>" }
    """
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"error": "refresh token required"}, status=400)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"detail": "Logged out"}, status=200)
        except Exception:
            return Response({"error": "invalid refresh token"}, status=400)
