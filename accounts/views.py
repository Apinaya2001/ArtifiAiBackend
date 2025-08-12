from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes

from .serializers import RegisterSerializer, UserMeSerializer, ChangePasswordSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
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

    s = UserMeSerializer(request.user)
    return Response(s.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response({"detail": "Password updated"}, status=status.HTTP_200_OK)
