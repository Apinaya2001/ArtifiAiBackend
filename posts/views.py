# # posts/views.py
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .models import Post, Like, Comment
# from .serializers import PostSerializer, CommentSerializer

# class PostViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = PostSerializer
#     queryset = Post.objects.select_related('user').prefetch_related('likes','comments').order_by('-created_at')

#     def get_serializer_context(self):
#         ctx = super().get_serializer_context()
#         ctx["request"] = self.request
#         return ctx

#     def perform_create(self, serializer):
#         serializer.save()  # user taken from context in serializer

#     @action(detail=True, methods=['post'])
#     def like(self, request, pk=None):
#         post = self.get_object()
#         Like.objects.get_or_create(user=request.user, post=post)
#         return Response({'ok': True})

#     @action(detail=True, methods=['post'])
#     def unlike(self, request, pk=None):
#         post = self.get_object()
#         Like.objects.filter(user=request.user, post=post).delete()
#         return Response({'ok': True})

#     @action(detail=True, methods=['post'])
#     def comment(self, request, pk=None):
#         post = self.get_object()
#         c = Comment.objects.create(user=request.user, post=post, text=request.data['text'])
#         return Response(CommentSerializer(c).data, status=status.HTTP_201_CREATED)
# posts/views.py  (no django_filters import needed)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Post, Like, Comment
from .serializers import PostSerializer, CommentSerializer

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = (
        Post.objects.select_related("user")
        .prefetch_related("likes", "comments")
        .order_by("-created_at")
    )

    # Public list/retrieve; auth for writes
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    # Built-in search/ordering only
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["caption"]
    ordering = ["-created_at"]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        qp = self.request.query_params

        # manual filters
        username = (qp.get("username") or "").strip()
        if username:
            qs = qs.filter(user__username__iexact=username)

        user_id = qp.get("user_id")
        if user_id and user_id.isdigit():
            qs = qs.filter(user_id=int(user_id))

        style = (qp.get("style") or "").strip()
        if style:
            qs = qs.filter(style__iexact=style)

        mine = (qp.get("mine") or "").lower()
        if mine in {"1", "true", "yes"} and self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)

        return qs

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def mine(self, request):
        qs = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        Like.objects.get_or_create(user=request.user, post=post)
        return Response({"ok": True}, status=200)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        Like.objects.filter(user=request.user, post=post).delete()
        return Response(status=204)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"detail": "text is required"}, status=400)
        post = self.get_object()
        c = Comment.objects.create(user=request.user, post=post, text=text)
        return Response(CommentSerializer(c).data, status=status.HTTP_201_CREATED)
