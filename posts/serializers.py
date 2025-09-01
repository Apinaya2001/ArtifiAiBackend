# posts/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Post, Comment

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name")

class CommentSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(read_only=True)

    class Meta:
        model = Comment
        # Safer to include everything — avoids guessing your field names
        fields = "__all__"
        # If your Comment model has these, they’ll be respected; otherwise ignored
        read_only_fields = ("author", "created_at", "updated_at")

class PostSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ("author", "created_at", "updated_at")

    def get_likes_count(self, obj):
        # Works whether you have a ManyToMany named 'likes' or not
        if hasattr(obj, "likes"):
            try:
                return obj.likes.count()
            except Exception:
                return 0
        return 0

    def get_comments_count(self, obj):
        # Try common related names; fall back to default comment_set
        for rel in ("comments", "comment_set"):
            if hasattr(obj, rel):
                try:
                    return getattr(obj, rel).count()
                except Exception:
                    return 0
        return 0
