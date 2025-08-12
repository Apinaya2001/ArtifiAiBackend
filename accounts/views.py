
# # accounts/views.py
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from django.db import IntegrityError

# from rest_framework.views import APIView
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status

# from rest_framework_simplejwt.tokens import RefreshToken


# # imports unchanged...

# def _tokens_for_user(user: User):
#     refresh = RefreshToken.for_user(user)
#     return str(refresh.access_token), str(refresh)

# class RegisterView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username    = (request.data.get("username") or "").strip()
#         email       = (request.data.get("email") or "").strip()
#         password    = request.data.get("password")
#         first_name  = (request.data.get("first_name") or "").strip()
#         last_name   = (request.data.get("last_name") or "").strip()

#         if not username or not password:
#             return Response({"detail": "username and password required"}, status=400)

#         try:
#             u = User.objects.create_user(username=username, email=email, password=password)
#             if first_name: u.first_name = first_name
#             if last_name:  u.last_name  = last_name
#             u.save()
#         except IntegrityError:
#             return Response({"detail": "username already exists"}, status=400)

#         access, refresh = _tokens_for_user(u)
#         full_name = (f"{u.first_name} {u.last_name}").strip() or u.username
#         return Response(
#             {
#                 "access": access,
#                 "refresh": refresh,
#                 "user": {
#                     "id": u.id,
#                     "username": u.username,
#                     "first_name": u.first_name,
#                     "last_name": u.last_name,
#                     "name": full_name,
#                     "email": u.email,
#                 },
#             },
#             status=status.HTTP_201_CREATED,
#         )

# @api_view(["POST"])
# @permission_classes([AllowAny])
# def login_view(request):
#     ident = request.data.get("username") or request.data.get("email")
#     password = request.data.get("password")
#     if not ident or not password:
#         return Response({"detail": "username/email and password required"}, status=400)

#     username = ident
#     if "@" in ident:
#         try:
#             username = User.objects.get(email__iexact=ident).username
#         except User.DoesNotExist:
#             pass

#     user = authenticate(request, username=username, password=password)
#     if not user:
#         return Response({"detail": "Invalid credentials"}, status=401)

#     access, refresh = _tokens_for_user(user)
#     full_name = (f"{user.first_name} {user.last_name}").strip() or user.username
#     return Response(
#         {
#             "access": access,
#             "refresh": refresh,
#             "user": {
#                 "id": user.id,
#                 "username": user.username,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "name": full_name,
#                 "email": user.email,
#             },
#         }
#     )

# class MeView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         u = request.user
#         return Response(
#             {
#                 "id": u.id,
#                 "username": u.username,
#                 "email": u.email,
#                 "first_name": u.first_name,
#                 "last_name": u.last_name,
#                 "name": (f"{u.first_name} {u.last_name}").strip() or u.username,
#             }
#         )
# accounts/views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.utils import timezone


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes

from .serializers import RegisterSerializer, UserMeSerializer, ChangePasswordSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username    = (request.data.get("username") or "").strip()
        email       = (request.data.get("email") or "").strip()
        password    = request.data.get("password")
        first_name  = (request.data.get("first_name") or "").strip()
        last_name   = (request.data.get("last_name") or "").strip()

        if not username or not password:
            return Response({"detail": "username and password required"}, status=400)

        try:
            u = User.objects.create_user(username=username, email=email, password=password)
            # save names if provided
            if first_name:
                u.first_name = first_name
            if last_name:
                u.last_name = last_name
            u.save()
        except IntegrityError:
            return Response({"detail": "username already exists"}, status=400)

        access, refresh = _tokens_for_user(u)
        full_name = (f"{u.first_name} {u.last_name}").strip() or u.username

        return Response(
            {
                "access": access,
                "refresh": refresh,
                "user": {
                    "id": u.id,
                    "username": u.username,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "name": full_name,
                    "email": u.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["GET", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def me_user(request):
    if request.method == "PATCH":
        s = UserMeSerializer(request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_200_OK)

    # Allow email login by mapping to username if an email was provided
    username = ident
    if "@" in ident:
        try:
            username = User.objects.get(email__iexact=ident).username
        except User.DoesNotExist:
            pass

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=401)

# ✅ manually update last_login
    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    access, refresh = _tokens_for_user(user)
    full_name = (f"{user.first_name} {user.last_name}").strip() or user.username

    return Response(
        {
            "access": access,
            "refresh": refresh,
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "name": full_name,
                "email": user.email,
            },
        }
    )


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "name": (f"{u.first_name} {u.last_name}").strip() or u.username,
            }
        )
