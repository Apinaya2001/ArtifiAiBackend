# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes

from .serializers import RegisterSerializer, UserMeSerializer, ChangePasswordSerializer


class RegisterView(APIView):
    """
    POST /api/accounts/register/
    -> creates a user, returns user info (no tokens)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if not s.is_valid():
            # return field errors so the client can show them
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

        user = s.save()
        return Response({"user": UserMeSerializer(user).data},
                        status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def me_user(request):
    if request.method == "PATCH":
        s = UserMeSerializer(request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=status.HTTP_200_OK)
    return Response(UserMeSerializer(request.user).data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={"request": request})
