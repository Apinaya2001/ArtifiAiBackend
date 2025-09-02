# from django.urls import path
# from .views import (
#     PostListCreateView,
#     ToggleLikeAPIView,
#     CommentListCreateAPIView,
# )

# urlpatterns = [
#     path("", PostListCreateView.as_view(), name="post-list-create"),
#     path("<int:pk>/like/", ToggleLikeAPIView.as_view(), name="post-like"),
#     path("<int:pk>/comments/", CommentListCreateAPIView.as_view(), name="post-comments"),
# ]
from django.urls import path
from .views import (
    PostListCreateView,
    PostDetailView,
    ToggleLikeAPIView,
    CommentListCreateAPIView,
)

urlpatterns = [
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:pk>/", PostDetailView.as_view(), name="post-detail"),           # <— add this
    path("<int:pk>/like/", ToggleLikeAPIView.as_view(), name="post-like"),
    path("<int:pk>/comments/", CommentListCreateAPIView.as_view(), name="post-comments"),
]
