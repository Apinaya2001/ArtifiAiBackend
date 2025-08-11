
# profiles/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Profile
from .serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Public list/retrieve, auth required for create/update/delete.

    Extra endpoints:
      - GET /api/profiles/me/                            -> current user's profile (auto-create if missing)
      - PATCH/PUT /api/profiles/me/                      -> update current user's profile (incl. images)
      - GET /api/profiles/by_username/?username=<name>   -> lookup by username
      - Filtering: /api/profiles/?username=<name>        -> case-insensitive filter
    """
    serializer_class = ProfileSerializer
    queryset = (
        Profile.objects
        .select_related("user")
        .prefetch_related("followers")
        .order_by("id")
    )

    # Public read, auth for writes
    def get_permissions(self):
        if self.action in ["list", "retrieve", "by_username"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    # Ensure absolute URLs for avatar/cover
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    # Optional filter: ?username=<name>
    def get_queryset(self):
        qs = super().get_queryset()
        username = (self.request.query_params.get("username") or "").strip()
        if username:
            qs = qs.filter(user__username__iexact=username)
        return qs

    # Ensure the creating user is set
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Prevent editing/deleting other users' profiles
    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.user_id != self.request.user.id:
            raise PermissionDenied("You can only edit your own profile.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            raise PermissionDenied("You can only delete your own profile.")
        instance.delete()

    # --- Extras ---

    @action(
        detail=False,
        methods=["get", "patch", "put"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """
        GET  -> return (and auto-create) the current user's profile
        PATCH/PUT -> update current user's profile (supports multipart for images)
        """
        profile, _ = Profile.objects.get_or_create(user=request.user)

        if request.method in ["PATCH", "PUT"]:
            partial = request.method == "PATCH"
            serializer = self.get_serializer(profile, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()  # perform_update will enforce ownership
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def by_username(self, request):
        """
        GET /api/profiles/by_username/?username=<name>
        Public lookup by username (case-insensitive).
        """
        username = (request.query_params.get("username") or "").strip()
        profile = get_object_or_404(
            Profile.objects.select_related("user"),
            user__username__iexact=username,
        )
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
