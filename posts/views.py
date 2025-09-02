
# # from django.db.models import Count
# # from rest_framework import generics, permissions, status
# # from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# # from rest_framework.response import Response
# # from rest_framework.views import APIView

# # from .models import Post, Like, Comment
# # from .serializers import PostSerializer, CommentSerializer


# # class PostListCreateView(generics.ListCreateAPIView):
# #     serializer_class   = PostSerializer
# #     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
# #     parser_classes     = [MultiPartParser, FormParser, JSONParser]

# #     def get_queryset(self):
# #         qs = (
# #             Post.objects
# #             .select_related("user", "user__profile")
# #             .annotate(likes_count=Count("likes"), comments_count=Count("comments"))
# #             .order_by("-created_at")
# #         )
# #         username = self.request.query_params.get("username")
# #         if username:
# #             qs = qs.filter(user__username=username)
# #         return qs

# #     def get_serializer_context(self):
# #         ctx = super().get_serializer_context()
# #         ctx["request"] = self.request
# #         return ctx


# # class ToggleLikeAPIView(APIView):
# #     permission_classes = [permissions.IsAuthenticated]

# #     def post(self, request, pk: int):
# #         try:
# #             post = Post.objects.get(pk=pk)
# #         except Post.DoesNotExist:
# #             return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

# #         like, created = Like.objects.get_or_create(user=request.user, post=post)
# #         liked = True
# #         if not created:
# #             like.delete()
# #             liked = False

# #         count = Like.objects.filter(post=post).count()
# #         return Response({"liked": liked, "likes_count": count})


# # class CommentListCreateAPIView(generics.ListCreateAPIView):
# #     serializer_class   = CommentSerializer
# #     permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# #     def get_queryset(self):
# #         return Comment.objects.filter(post_id=self.kwargs["pk"]).select_related("user").order_by("created_at")

# #     def perform_create(self, serializer):
# #         if not self.request.user.is_authenticated:
# #             raise PermissionError("Auth required")
# #         serializer.save(user=self.request.user, post_id=self.kwargs["pk"])

# #     def get_serializer_context(self):
# #         ctx = super().get_serializer_context()
# #         ctx["request"] = self.request
# #         return ctx
# from django.db.models import Count, Exists, OuterRef, Value, BooleanField
# from rest_framework import generics, permissions, status
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from .models import Post, Like, Comment
# from .serializers import PostSerializer, CommentSerializer


# def annotated_posts(request):
#     user = getattr(request, "user", None)
#     liked_subq = Like.objects.filter(post_id=OuterRef("pk"))
#     if user and user.is_authenticated:
#         liked_subq = liked_subq.filter(user_id=user.id)

#     return (
#         Post.objects
#         .select_related("user", "user__profile")
#         # IMPORTANT: distinct=True prevents inflated counts when both relations are joined
#         .annotate(
#             likes_count=Count("likes", distinct=True),
#             comments_count=Count("comments", distinct=True),
#             liked=Exists(liked_subq) if (user and user.is_authenticated)
#                   else Value(False, output_field=BooleanField()),
#         )
#         .order_by("-created_at")
#     )


# class PostListCreateView(generics.ListCreateAPIView):
#     serializer_class   = PostSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#     parser_classes     = [MultiPartParser, FormParser, JSONParser]

#     def get_queryset(self):
#         qs = annotated_posts(self.request)
#         username = self.request.query_params.get("username")
#         if username:
#             qs = qs.filter(user__username=username)
#         return qs

#     def get_serializer_context(self):
#         ctx = super().get_serializer_context()
#         ctx["request"] = self.request
#         return ctx


# class PostDetailView(generics.RetrieveAPIView):
#     serializer_class   = PostSerializer
#     permission_classes = [permissions.AllowAny]

#     def get_queryset(self):
#         return annotated_posts(self.request)

#     def get_serializer_context(self):
#         ctx = super().get_serializer_context()
#         ctx["request"] = self.request
#         return ctx


# class ToggleLikeAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, pk: int):
#         try:
#             post = Post.objects.get(pk=pk)
#         except Post.DoesNotExist:
#             return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

#         like, created = Like.objects.get_or_create(user=request.user, post=post)
#         liked = True
#         if not created:
#             like.delete()
#             liked = False

#         count = Like.objects.filter(post=post).count()
#         return Response({"liked": liked, "likes_count": count})


# class CommentListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class   = CommentSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]

#     def get_queryset(self):
#         return (Comment.objects
#                 .filter(post_id=self.kwargs["pk"])
#                 .select_related("user")
#                 .order_by("-created_at"))  # newest first in the modal

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user, post_id=self.kwargs["pk"])

#     def get_serializer_context(self):
#         ctx = super().get_serializer_context()
#         ctx["request"] = self.request
#         return ctx
from django.db.models import Count, Exists, OuterRef, Value, BooleanField
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post, Like, Comment
from .serializers import PostSerializer, CommentSerializer


def annotated_posts(request):
    """
    Shared queryset: includes counts and a per-request-user 'liked' boolean.
    DISTINCT is important to avoid inflated counts when multiple joins occur.
    """
    user = getattr(request, "user", None)
    liked_subq = Like.objects.filter(post_id=OuterRef("pk"))
    if user and user.is_authenticated:
        liked_subq = liked_subq.filter(user_id=user.id)

    return (
        Post.objects
        .select_related("user", "user__profile")
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
            liked=Exists(liked_subq) if (user and user.is_authenticated)
                  else Value(False, output_field=BooleanField()),
        )
        .order_by("-created_at")
    )


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = annotated_posts(self.request)
        username = self.request.query_params.get("username")
        if username:
            qs = qs.filter(user__username=username)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class PostDetailView(generics.RetrieveAPIView):
    serializer_class   = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return annotated_posts(self.request)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class ToggleLikeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=request.user, post=post)
        liked = True
        if not created:
            like.delete()
            liked = False

        count = Like.objects.filter(post=post).count()
        return Response({"liked": liked, "likes_count": count})


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class   = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return (
            Comment.objects
            .filter(post_id=self.kwargs["pk"])
            .select_related("user")
            .order_by("-created_at")   # newest first in modal
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, post_id=self.kwargs["pk"])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
