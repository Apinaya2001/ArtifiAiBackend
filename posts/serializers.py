# # # posts/serializers.py
# # from rest_framework import serializers
# # from .models import Post, Comment



# # class PostSerializer(serializers.ModelSerializer):
# #     username = serializers.CharField(source='user.username', read_only=True)
# #     likes = serializers.IntegerField(source='likes.count', read_only=True)
# #     comments = CommentSerializer(many=True, read_only=True)
# #     class Meta:
# #         model = Post
# #         fields = ('id','username','image','caption','style','tags','created_at','likes','comments')
# from urllib.parse import urlparse
# from pathlib import Path
# from django.conf import settings
# from django.core.files import File
# from rest_framework import serializers
# from .models import Comment, Post

# def _rel_from_url(url_or_path: str) -> str:
#     if not url_or_path:
#         return ""
#     p = urlparse(url_or_path)
#     path = p.path or url_or_path
#     media = (settings.MEDIA_URL or "/media/").rstrip("/")
#     return path.replace(media, "", 1).lstrip("/")

# class CommentSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source='user.username', read_only=True)
#     class Meta: model = Comment; fields = ('id','username','text','created_at')

# class PostSerializer(serializers.ModelSerializer):
#     # allow JSON lists for tags even with multipart
#     tags = serializers.ListField(child=serializers.CharField(), required=False)
#     # new: accept a URL/path instead of uploading a file
#     image_url = serializers.CharField(write_only=True, required=False, allow_blank=True)

#     class Meta:
#         model = Post
#         fields = ["id", "image", "image_url", "caption", "style", "tags", "created_at", "user_id"]
#         read_only_fields = ["id", "created_at", "user_id", "image"]

#     def create(self, validated_data):
#         image_file = self.initial_data.get("image")  # may be upload in multipart
#         image_url  = validated_data.pop("image_url", "")
#         user = self.context["request"].user

#         post = Post(
#             user=user,
#             caption=validated_data.get("caption", ""),
#             style=validated_data.get("style", ""),
#             tags=validated_data.get("tags", []),
#         )

#         if image_file and hasattr(image_file, "read"):
#             # standard upload path
#             post.image = image_file
#             post.save()
#             return post

#         # else: copy an existing styled file from MEDIA_ROOT using image_url
#         rel = _rel_from_url(image_url)
#         if not rel:
#             raise serializers.ValidationError({"image_url": "Provide image or image_url"})

#         src = Path(settings.MEDIA_ROOT) / rel
#         if not src.exists():
#             raise serializers.ValidationError({"image_url": f"Not found: {rel}"})

#         with open(src, "rb") as fh:
#             # keep a clean copy under posts/
#             post.image.save(f"posts/{src.stem}.jpg", File(fh), save=True)

#         return post
# posts/serializers.py
from urllib.parse import urlparse
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Comment, Post

def _rel_from_url(url_or_path: str) -> str:
    if not url_or_path:
        return ""
    p = urlparse(url_or_path)
    path = p.path or url_or_path
    media = (settings.MEDIA_URL or "/media/").rstrip("/")
    return path.replace(media, "", 1).lstrip("/")

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name")

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Comment
        fields = ("id", "username", "text", "created_at")

class PostSerializer(serializers.ModelSerializer):
    # read
    user = UserMiniSerializer(read_only=True)
    image = serializers.ImageField(use_url=True, read_only=True)  # will return URL when request is in context
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    # write
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    image_url = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Post
        fields = [
            "id", "user", "user_id",
            "image", "image_url",
            "caption", "style", "tags",
            "likes_count", "comments",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user", "user_id", "image", "likes_count", "comments"]

    def create(self, validated_data):
        image_file = self.initial_data.get("image")  # may be upload in multipart
        image_url  = validated_data.pop("image_url", "")
        user = self.context["request"].user

        post = Post(
            user=user,
            caption=validated_data.get("caption", ""),
            style=validated_data.get("style", ""),
            tags=validated_data.get("tags", []),
        )

        if image_file and hasattr(image_file, "read"):
            # standard upload path
            post.image = image_file
            post.save()
            return post

        # else: copy an existing styled file from MEDIA_ROOT using image_url
        rel = _rel_from_url(image_url)
        if not rel:
            raise serializers.ValidationError({"image_url": "Provide image or image_url"})

        src = Path(settings.MEDIA_ROOT) / rel
        if not src.exists():
            raise serializers.ValidationError({"image_url": f"Not found: {rel}"})

        with open(src, "rb") as fh:
            # keep a clean copy under posts/
            post.image.save(f"posts/{src.stem}.jpg", File(fh), save=True)

        return post
