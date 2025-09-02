from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Conversation, ConversationState, Message

User = get_user_model()


def profile_snippet(user, request):
    # Adjust this to your actual Profile model/fields if different
    name = getattr(user, "name", None) or f"{user.first_name} {user.last_name}".strip() or user.username
    avatar = None
    prof = getattr(user, "profile", None)
    if prof and getattr(prof, "avatar", None):
        try:
            avatar = request.build_absolute_uri(prof.avatar.url)
        except Exception:
            avatar = None
    return {"username": user.username, "name": name, "avatar": avatar}


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "sender", "text", "image", "created", "is_own"]

    def get_sender(self, obj):
        return obj.sender.username

    def get_image(self, obj):
        if not obj.image:
            return None
        req = self.context.get("request")
        return req.build_absolute_uri(obj.image.url) if req else obj.image.url

    def get_is_own(self, obj):
        req = self.context.get("request")
        return bool(req and req.user and req.user.id == obj.sender_id)


class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "other_user", "last_message", "unread"]

    def get_other_user(self, obj):
        req = self.context["request"]
        return profile_snippet(obj.other_for(req.user), req)

    def get_last_message(self, obj):
        m = obj.messages.first()  # newest due to ordering
        if not m:
            return None
        return {"text": m.text or ("📷 Photo" if m.image else ""), "created": m.created}

    def get_unread(self, obj):
        req = self.context["request"]
        # messages from the other user, created after last_read_at
        try:
            st = ConversationState.objects.get(conversation=obj, user=req.user)
            since = st.last_read_at
        except ConversationState.DoesNotExist:
            since = None
        qs = obj.messages.exclude(sender=req.user)
        if since:
            qs = qs.filter(created__gt=since)
        return qs.count()
