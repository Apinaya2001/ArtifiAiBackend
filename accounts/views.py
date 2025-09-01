# accounts/views.py
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer  # <-- for refresh

from .serializers import RegisterSerializer, LoginSerializer, UserMeSerializer, ChangePasswordSerializer

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])                     # <-- ignore Authorization header
def register(request):
    s = RegisterSerializer(data=request.data)
    if not s.is_valid():
        return Response(s.errors, status=400)
    user = s.save()
    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "registered",
        "user": UserMeSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }, status=201)

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])                     # <-- ignore Authorization header
def login(request):
    s = LoginSerializer(data=request.data)
    if not s.is_valid():
        return Response(s.errors, status=400)
    user = s.validated_data["user"]
    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "logged_in",
        "user": UserMeSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }, status=200)

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])                     # <-- public refresh
def refresh(request):
    """
    Body: { "refresh": "<refresh_token>" }
    Returns: { "access": "<new_access>", "refresh": "<rotated_refresh>"? }
    (Rotation depends on SIMPLE_JWT settings.)
    """
    serializer = TokenRefreshSerializer(data={"refresh": request.data.get("refresh", "")})
    try:
        serializer.is_valid(raise_exception=True)
    except Exception:
        return Response({"error": "invalid refresh token"}, status=401)
    return Response(serializer.validated_data, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserMeSerializer(request.user).data, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    s = ChangePasswordSerializer(data=request.data)
    if not s.is_valid():
        return Response(s.errors, status=400)
    user = request.user
    if not user.check_password(s.validated_data["old_password"]):
        return Response({"old_password": ["Wrong password"]}, status=400)
    user.set_password(s.validated_data["new_password"])
    user.save()
    return Response({"message": "password_changed"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    all_tokens = str(request.data.get("all", "")).lower() in ("1","true","yes")
    try:
        if all_tokens:
            for tok in OutstandingToken.objects.filter(user=request.user):
                BlacklistedToken.objects.get_or_create(token=tok)
        else:
            refresh = request.data.get("refresh")
            if not refresh:
                return Response({"error": "refresh token required"}, status=400)
            RefreshToken(refresh).blacklist()
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    return Response({"message": "logged_out"}, status=200)
