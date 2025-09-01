# # profiles/serializers.py
# from __future__ import annotations
# from typing import Any
# from django.utils.translation import gettext_lazy as _
# from rest_framework import serializers
# from .models import Profile,Follow

# MAX_UPLOAD_MB = 10
# ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


# class ProfileSerializer(serializers.ModelSerializer):
#     username   = serializers.SerializerMethodField(read_only=True)
#     avatar_url = serializers.SerializerMethodField(read_only=True)
#     cover_url  = serializers.SerializerMethodField(read_only=True)
#     joined     = serializers.SerializerMethodField(read_only=True)
#     followers_count = serializers.SerializerMethodField(read_only=True)
#     following_count = serializers.SerializerMethodField(read_only=True)
#     is_following    = serializers.SerializerMethodField(read_only=True)

#     # UI uses "name"
#     name = serializers.CharField(source="display_name", required=False, allow_blank=True)

#     class Meta:
#         model = Profile
#         fields = [
#             "id",
#             "username",
#             "display_name", "name",
#             "bio", "location",
#             "avatar", "cover",
#             "avatar_url", "cover_url", "joined",
#              "followers_count", "following_count", "is_following",
#             "created_at", "updated_at",
#         ]
#         read_only_fields = [
#             "id", "username", "avatar_url", "cover_url", "joined", "created_at", "updated_at",
#               "followers_count","following_count","is_following",
#         ]
#         extra_kwargs = {
#             "display_name": {"required": False, "allow_blank": True},
#             "bio":          {"required": False, "allow_blank": True},
#             "location":     {"required": False, "allow_blank": True},
#             "avatar":       {"required": False, "allow_null": True},
#             "cover":        {"required": False, "allow_null": True},
#         }

#     # ----- helpers -----
#     def get_username(self, obj: Profile) -> str:
#         return obj.user.username

#     def _abs(self, f) -> str:
#         try:
#             if not f:
#                 return ""
#             request = self.context.get("request")
#             url = f.url
#             return request.build_absolute_uri(url) if request else url
#         except Exception:
#             return ""

#     def get_avatar_url(self, obj: Profile) -> str:
#         return self._abs(obj.avatar)

#     def get_cover_url(self, obj: Profile) -> str:
#         return self._abs(obj.cover)

#     def get_joined(self, obj: Profile) -> str:
#         try:
#             return obj.user.date_joined.isoformat()
#         except Exception:
#             return ""
        
        
# def get_followers_count(self, obj: Profile) -> int:
#         return Follow.objects.filter(following=obj.user_id).count()

# def get_following_count(self, obj: Profile) -> int:
#         return Follow.objects.filter(follower=obj.user_id).count()


# def get_is_following(self, obj: Profile) -> bool:
#         req = self.context.get("request")
#         if not req or not req.user.is_authenticated or req.user_id == obj.user_id:
#             return False
#         return Follow.objects.filter(follower=req.user_id, following=obj.user_id).exists()




#      # -------- validation
# def _validate_upload(self, f, field_name: str) -> None:
#         if not f:
#             return
#         try:
#             size_mb = (getattr(f, "size", 0) or 0) / (1024 * 1024)
#             if MAX_UPLOAD_MB and size_mb > MAX_UPLOAD_MB:
#                 raise serializers.ValidationError({field_name: _(f"File too large (> {MAX_UPLOAD_MB} MB).")})
#         except Exception:
#             pass
#         ctype = getattr(f, "content_type", "") or ""
#         if ALLOWED_IMAGE_TYPES and ctype and ctype not in ALLOWED_IMAGE_TYPES:
#             raise serializers.ValidationError({field_name: _("Unsupported image type.")})

# def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
#         for key in ("display_name", "bio", "location"):
#             if key in attrs and isinstance(attrs[key], str):
#                 attrs[key] = attrs[key].strip()
#         if "avatar" in attrs:
#             self._validate_upload(attrs["avatar"], "avatar")
#         if "cover" in attrs:
#             self._validate_upload(attrs["cover"], "cover")
#         return attrs

#     # -------- representation
# def to_representation(self, instance: Profile) -> dict[str, Any]:
#         data = super().to_representation(instance)
#         try:
#             ver = instance.updated_at.strftime("%Y%m%d%H%M%S%f")
#         except Exception:
#             ver = ""

#         avatar_abs = self._abs(instance.avatar)
#         cover_abs  = self._abs(instance.cover)
#         if avatar_abs and ver:
#             avatar_abs = f"{avatar_abs}?v={ver}"
#         if cover_abs and ver:
#             cover_abs = f"{cover_abs}?v={ver}"

#         data["avatar"] = avatar_abs
#         data["cover"]  = cover_abs
#         data["name"]   = (data.get("name") or data.get("display_name") or "").strip()
#         if not data.get("joined"):
#             data["joined"] = self.get_joined(instance)
#         return data

#     # -------- update
# def update(self, instance: Profile, validated: dict[str, Any]) -> Profile:
#         for f in ("display_name", "bio", "location"):
#             if f in validated:
#                 setattr(instance, f, validated.get(f) or "")
#         sentinel = serializers.empty
#         avatar = validated.get("avatar", sentinel)
#         cover  = validated.get("cover", sentinel)
#         if avatar is not sentinel:
#             instance.avatar = avatar
#         if cover is not sentinel:
#             instance.cover = cover
#         instance.save()
#         return instance

# profiles/serializers.py
from __future__ import annotations
from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Profile, Follow

MAX_UPLOAD_MB = 10
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class ProfileSerializer(serializers.ModelSerializer):
    username   = serializers.SerializerMethodField(read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)
    cover_url  = serializers.SerializerMethodField(read_only=True)
    joined     = serializers.SerializerMethodField(read_only=True)

    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)
    is_following    = serializers.SerializerMethodField(read_only=True)

    # UI can send "name" instead of "display_name"
    name = serializers.CharField(source="display_name", required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = [
            "id", "username",
            "display_name", "name",
            "bio", "location",
            "avatar", "cover",
            "avatar_url", "cover_url", "joined",
            "followers_count", "following_count", "is_following",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id","username","avatar_url","cover_url","joined",
            "followers_count","following_count","is_following",
            "created_at","updated_at",
        ]
        extra_kwargs = {
            "display_name": {"required": False, "allow_blank": True},
            "bio":          {"required": False, "allow_blank": True},
            "location":     {"required": False, "allow_blank": True},
            "avatar":       {"required": False, "allow_null": True},
            "cover":        {"required": False, "allow_null": True},
        }

    # ---------- READ helpers ----------
    def get_username(self, obj: Profile) -> str:
        return obj.user.username

    def _abs(self, f) -> str:
        try:
            if not f:
                return ""
            request = self.context.get("request")
            url = f.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return ""

    def get_avatar_url(self, obj: Profile) -> str:
        return self._abs(obj.avatar)

    def get_cover_url(self, obj: Profile) -> str:
        return self._abs(obj.cover)

    def get_joined(self, obj: Profile) -> str:
        try:
            return obj.user.date_joined.isoformat()
        except Exception:
            return ""

    def get_followers_count(self, obj: Profile) -> int:
        return Follow.objects.filter(following=obj.user).count()

    def get_following_count(self, obj: Profile) -> int:
        return Follow.objects.filter(follower=obj.user).count()

    def get_is_following(self, obj: Profile) -> bool:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(follower=request.user, following=obj.user).exists()

    # ---------- validation ----------
    def _validate_upload(self, f, field_name: str) -> None:
        if not f:
            return
        try:
            size_mb = (getattr(f, "size", 0) or 0) / (1024 * 1024)
            if MAX_UPLOAD_MB and size_mb > MAX_UPLOAD_MB:
                raise serializers.ValidationError({field_name: _(f"File too large (> {MAX_UPLOAD_MB} MB).")})
        except Exception:
            pass
        ctype = getattr(f, "content_type", "") or ""
        if ALLOWED_IMAGE_TYPES and ctype and ctype not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError({field_name: _("Unsupported image type.")})

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        for key in ("display_name", "bio", "location"):
            if key in attrs and isinstance(attrs[key], str):
                attrs[key] = attrs[key].strip()
        if "avatar" in attrs:
            self._validate_upload(attrs["avatar"], "avatar")
        if "cover" in attrs:
            self._validate_upload(attrs["cover"], "cover")
        return attrs

    # ---------- out ----------
    def to_representation(self, instance: Profile) -> dict[str, Any]:
        data = super().to_representation(instance)
        try:
            ver = instance.updated_at.strftime("%Y%m%d%H%M%S%f")
        except Exception:
            ver = ""
        a = self._abs(instance.avatar)
        c = self._abs(instance.cover)
        if a and ver: a = f"{a}?v={ver}"
        if c and ver: c = f"{c}?v={ver}"
        data["avatar"] = a
        data["cover"]  = c
        data["name"]   = (data.get("name") or data.get("display_name") or "").strip()
        if not data.get("joined"):
            data["joined"] = self.get_joined(instance)
        return data

    # ---------- update ----------
    def update(self, instance: Profile, validated: dict[str, Any]) -> Profile:
        for f in ("display_name", "bio", "location"):
            if f in validated:
                setattr(instance, f, validated.get(f) or "")
        sentinel = serializers.empty
        avatar = validated.get("avatar", sentinel)
        cover  = validated.get("cover", sentinel)
        if avatar is not sentinel:
            instance.avatar = avatar
        if cover is not sentinel:
            instance.cover = cover
        instance.save()
        return instance
