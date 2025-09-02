
# # from __future__ import annotations
# # import json, re
# # from urllib.parse import urlparse

# # from django.conf import settings
# # from rest_framework import serializers

# # from .models import Post, Like, Comment


# # class CommentSerializer(serializers.ModelSerializer):
# #     user = serializers.SerializerMethodField(read_only=True)

# #     class Meta:
# #         model = Comment
# #         fields = ["id", "text", "created_at", "user"]

# #     def get_user(self, obj: Comment):
# #         u = obj.user
# #         req = self.context.get("request")
# #         avatar = ""
# #         try:
# #             prof = getattr(u, "profile", None)
# #             if prof and prof.avatar:
# #                 avatar = prof.avatar.url
# #                 if req:
# #                     avatar = req.build_absolute_uri(avatar)
# #         except Exception:
# #             pass
# #         return {"username": u.username, "avatar": avatar}


# # class PostSerializer(serializers.ModelSerializer):
# #     # write
# #     image = serializers.ImageField(required=False, allow_null=True)
# #     image_url = serializers.CharField(write_only=True, required=False, allow_blank=True)
# #     caption = serializers.CharField(required=False, allow_blank=True)
# #     style   = serializers.CharField(required=False, allow_blank=True)
# #     tags    = serializers.ListField(child=serializers.CharField(), required=False)

# #     # read
# #     username  = serializers.CharField(source="user.username", read_only=True)
# #     user      = serializers.SerializerMethodField(read_only=True)   # { username, avatar }
# #     image_abs = serializers.SerializerMethodField(read_only=True)   # absolute url
# #     likes_count    = serializers.IntegerField(read_only=True)
# #     comments_count = serializers.IntegerField(read_only=True)
# #     liked          = serializers.SerializerMethodField(read_only=True)

# #     class Meta:
# #         model  = Post
# #         fields = [
# #             "id",
# #             # write
# #             "image", "image_url", "caption", "style", "tags",
# #             # read
# #             "username", "user", "image_abs", "created_at",
# #             "likes_count", "comments_count", "liked",
# #         ]
# #         read_only_fields = [
# #             "username", "user", "image_abs", "created_at",
# #             "likes_count", "comments_count", "liked",
# #         ]

# #     # ---------------- helpers ----------------
# #     def _abs_file(self, f) -> str:
# #         if not f:
# #             return ""
# #         try:
# #             url = f.url
# #         except Exception:
# #             url = str(f)
# #         if not url:
# #             return ""
# #         req = self.context.get("request")
# #         return req.build_absolute_uri(url) if req else url

# #     def _relpath_from_url(self, u: str) -> str:
# #         if not u:
# #             return ""
# #         path = urlparse(u).path if "://" in u else u
# #         path = path.lstrip("/")
# #         media_prefix = (settings.MEDIA_URL or "/media/").lstrip("/")
# #         if path.startswith(media_prefix):
# #             path = path[len(media_prefix):]
# #         return path

# #     def _normalize_tags(self, raw):
# #         if raw is None:
# #             return []
# #         if isinstance(raw, list):
# #             return [str(x).strip() for x in raw if str(x).strip()]
# #         if isinstance(raw, str):
# #             try:
# #                 j = json.loads(raw)
# #                 if isinstance(j, list):
# #                     return [str(x).strip() for x in j if str(x).strip()]
# #             except Exception:
# #                 pass
# #             return [s.lstrip("#").strip() for s in re.split(r"[\s,]+", raw) if s.strip()]
# #         return []

# #     # ---------------- validation ----------------
# #     def validate(self, attrs):
# #         img     = attrs.get("image")
# #         img_url = attrs.pop("image_url", "")

# #         if not img and not img_url:
# #             raise serializers.ValidationError({"image": "Provide either 'image' or 'image_url'."})

# #         attrs["_image_url"] = img_url

# #         if "tags" in attrs:
# #             attrs["tags"] = self._normalize_tags(attrs["tags"])

# #         return attrs

# #     # ---------------- create ----------------
# #     def create(self, validated):
# #         request = self.context.get("request")
# #         user = request.user if request else None
# #         if not user or not user.is_authenticated:
# #             raise serializers.ValidationError({"detail": "Auth required."})

# #         img_url = validated.pop("_image_url", "")
# #         image   = validated.get("image", None)

# #         post = Post(user=user, **validated)

# #         if not image and img_url:
# #             rel = self._relpath_from_url(img_url)
# #             if not rel:
# #                 raise serializers.ValidationError({"image_url": "Invalid or unsupported image_url."})
# #             post.image.name = rel

# #         post.save()
# #         return post

# #     # ---------------- representation ----------------
# #     def get_user(self, obj: Post) -> dict:
# #         prof = getattr(obj.user, "profile", None)
# #         avatar = self._abs_file(getattr(prof, "avatar", None)) if prof else ""
# #         return {"username": obj.user.username, "avatar": avatar}

# #     def get_image_abs(self, obj: Post) -> str:
# #         return self._abs_file(obj.image)

# #     def get_liked(self, obj: Post) -> bool:
# #         req = self.context.get("request")
# #         if not req or not req.user.is_authenticated:
# #             return False
# #         return Like.objects.filter(user=req.user, post=obj).exists()
# from __future__ import annotations
# import json, re
# from urllib.parse import urlparse

# from django.conf import settings
# from rest_framework import serializers

# from .models import Post, Like, Comment


# class CommentSerializer(serializers.ModelSerializer):
#     user = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = Comment
#         fields = ["id", "text", "created_at", "user"]

#     def get_user(self, obj: Comment):
#         u = obj.user
#         req = self.context.get("request")
#         avatar = ""
#         try:
#             prof = getattr(u, "profile", None)
#             if prof and prof.avatar:
#                 avatar = prof.avatar.url
#                 if req:
#                     avatar = req.build_absolute_uri(avatar)
#         except Exception:
#             pass
#         return {"username": u.username, "avatar": avatar}


# class PostSerializer(serializers.ModelSerializer):
#     # write
#     image = serializers.ImageField(required=False, allow_null=True)
#     image_url = serializers.CharField(write_only=True, required=False, allow_blank=True)
#     caption = serializers.CharField(required=False, allow_blank=True)
#     style   = serializers.CharField(required=False, allow_blank=True)
#     tags    = serializers.ListField(child=serializers.CharField(), required=False)

#     # read
#     username   = serializers.CharField(source="user.username", read_only=True)
#     user       = serializers.SerializerMethodField(read_only=True)
#     image_abs  = serializers.SerializerMethodField(read_only=True)
#     likes_count    = serializers.IntegerField(read_only=True)
#     comments_count = serializers.IntegerField(read_only=True)
#     liked          = serializers.BooleanField(read_only=True)   # <— annotated in queryset

#     class Meta:
#         model  = Post
#         fields = [
#             "id",
#             "image", "image_url", "caption", "style", "tags",
#             "username", "user", "image_abs", "created_at",
#             "likes_count", "comments_count", "liked",
#         ]
#         read_only_fields = [
#             "username", "user", "image_abs", "created_at",
#             "likes_count", "comments_count", "liked",
#         ]

#     # helpers
#     def _abs_file(self, f) -> str:
#         if not f: return ""
#         try: url = f.url
#         except Exception: url = str(f)
#         if not url: return ""
#         req = self.context.get("request")
#         return req.build_absolute_uri(url) if req else url

#     def _relpath_from_url(self, u: str) -> str:
#         if not u: return ""
#         path = urlparse(u).path if "://" in u else u
#         path = path.lstrip("/")
#         media_prefix = (settings.MEDIA_URL or "/media/").lstrip("/")
#         if path.startswith(media_prefix):
#             path = path[len(media_prefix):]
#         return path

#     def _normalize_tags(self, raw):
#         if raw is None: return []
#         if isinstance(raw, list):
#             return [str(x).strip() for x in raw if str(x).strip()]
#         if isinstance(raw, str):
#             try:
#                 j = json.loads(raw)
#                 if isinstance(j, list):
#                     return [str(x).strip() for x in j if str(x).strip()]
#             except Exception:
#                 pass
#             return [s.lstrip("#").strip() for s in re.split(r"[\s,]+", raw) if s.strip()]
#         return []

#     def validate(self, attrs):
#         img     = attrs.get("image")
#         img_url = attrs.pop("image_url", "")
#         if not img and not img_url:
#             raise serializers.ValidationError({"image": "Provide either 'image' or 'image_url'."})
#         attrs["_image_url"] = img_url
#         if "tags" in attrs:
#             attrs["tags"] = self._normalize_tags(attrs["tags"])
#         return attrs

#     def create(self, validated):
#         request = self.context.get("request")
#         user = request.user if request else None
#         if not user or not user.is_authenticated:
#             raise serializers.ValidationError({"detail": "Auth required."})

#         img_url = validated.pop("_image_url", "")
#         image   = validated.get("image", None)

#         post = Post(user=user, **validated)

#         if not image and img_url:
#             rel = self._relpath_from_url(img_url)
#             if not rel:
#                 raise serializers.ValidationError({"image_url": "Invalid or unsupported image_url."})
#             post.image.name = rel

#         post.save()
#         return post

#     def get_user(self, obj: Post) -> dict:
#         prof = getattr(obj.user, "profile", None)
#         avatar = self._abs_file(getattr(prof, "avatar", None)) if prof else ""
#         return {"username": obj.user.username, "avatar": avatar}

#     def get_image_abs(self, obj: Post) -> str:
#         return self._abs_file(obj.image)
from __future__ import annotations
import json, re
from urllib.parse import urlparse

from django.conf import settings
from rest_framework import serializers

from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "text", "created_at", "user"]

    def get_user(self, obj: Comment):
        u = obj.user
        req = self.context.get("request")
        avatar = ""
        try:
            prof = getattr(u, "profile", None)
            if prof and prof.avatar:
                avatar = prof.avatar.url
                if req:
                    avatar = req.build_absolute_uri(avatar)
        except Exception:
            pass
        return {"username": u.username, "avatar": avatar}


class PostSerializer(serializers.ModelSerializer):
    # ---------- write inputs ----------
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.CharField(write_only=True, required=False, allow_blank=True)
    caption = serializers.CharField(required=False, allow_blank=True)
    style   = serializers.CharField(required=False, allow_blank=True)
    tags    = serializers.ListField(child=serializers.CharField(), required=False)

    # ---------- read outputs ----------
    username   = serializers.CharField(source="user.username", read_only=True)
    user       = serializers.SerializerMethodField(read_only=True)   # { username, avatar }
    image_abs  = serializers.SerializerMethodField(read_only=True)   # absolute url
    likes_count    = serializers.IntegerField(read_only=True, default=0)
    comments_count = serializers.IntegerField(read_only=True, default=0)
    liked          = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model  = Post
        fields = [
            "id",
            # write
            "image", "image_url", "caption", "style", "tags",
            # read
            "username", "user", "image_abs", "created_at",
            "likes_count", "comments_count", "liked",
        ]
        read_only_fields = [
            "username", "user", "image_abs", "created_at",
            "likes_count", "comments_count", "liked",
        ]

    # ---------- helpers ----------
    def _abs_file(self, f) -> str:
        if not f:
            return ""
        try:
            url = f.url
        except Exception:
            url = str(f)
        if not url:
            return ""
        req = self.context.get("request")
        return req.build_absolute_uri(url) if req else url

    def _relpath_from_url(self, u: str) -> str:
        # 'http://host/media/foo.jpg' or '/media/foo.jpg' => 'foo.jpg'
        if not u:
            return ""
        path = urlparse(u).path if "://" in u else u
        path = path.lstrip("/")
        media_prefix = (settings.MEDIA_URL or "/media/").lstrip("/")
        if path.startswith(media_prefix):
            path = path[len(media_prefix):]
        return path

    def _normalize_tags(self, raw):
        if raw is None:
            return []
        if isinstance(raw, list):
            return [str(x).strip() for x in raw if str(x).strip()]
        if isinstance(raw, str):
            try:
                j = json.loads(raw)
                if isinstance(j, list):
                    return [str(x).strip() for x in j if str(x).strip()]
            except Exception:
                pass
            return [s.lstrip("#").strip() for s in re.split(r"[\s,]+", raw) if s.strip()]
        return []

    # ---------- validation ----------
    def validate(self, attrs):
        img     = attrs.get("image")
        img_url = attrs.pop("image_url", "")

        if not img and not img_url:
            raise serializers.ValidationError({"image": "Provide either 'image' or 'image_url'."})

        attrs["_image_url"] = img_url
        if "tags" in attrs:
            attrs["tags"] = self._normalize_tags(attrs["tags"])
        return attrs

    # ---------- create ----------
    def create(self, validated):
        request = self.context.get("request")
        user = request.user if request else None
        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": "Auth required."})

        img_url = validated.pop("_image_url", "")
        image   = validated.get("image", None)

        post = Post(user=user, **validated)

        if not image and img_url:
            rel = self._relpath_from_url(img_url)
            if not rel:
                raise serializers.ValidationError({"image_url": "Invalid or unsupported image_url."})
            post.image.name = rel

        post.save()
        return post

    # ---------- representation ----------
    def get_user(self, obj: Post) -> dict:
        prof = getattr(obj.user, "profile", None)
        avatar = self._abs_file(getattr(prof, "avatar", None)) if prof else ""
        return {"username": obj.user.username, "avatar": avatar}

    def get_image_abs(self, obj: Post) -> str:
        return self._abs_file(obj.image)
