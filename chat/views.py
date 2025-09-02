# chat/views.py
from django.contrib.auth import get_user_model
from django.db.models import Max, F
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Conversation, Message

User = get_user_model()

def _simple_user(u):
    if not u: return None
    # adapt keys to what your frontend expects
    return {
        "username": getattr(u, "username", ""),
        "name": getattr(u, "name", "") or getattr(u, "username", ""),
        "avatar": getattr(u, "avatar", None),  # if your User has avatar field
    }

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    """
    GET /api/chat/conversations/
    """
    qs = (
        Conversation.objects.filter(participants=request.user)
        .annotate(last_created=Max("messages__created"))  # ← correct related path
        .order_by(F("last_created").desc(nulls_last=True), "-id")
        .prefetch_related("participants")
    )

    out = []
    for c in qs:
        other = c.participants.exclude(id=request.user.id).first()
        last = c.messages.order_by("-created").first()
        out.append({
            "id": c.id,
            "other_user": _simple_user(other),
            "last_message": (
                {"id": last.id, "text": last.text or "", "created": last.created}
                if last else None
            ),
            "unread": 0,  # add tracking later if you want
        })
    return Response(out)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def conversation_messages(request, pk):
    """
    GET  /api/chat/conversations/<pk>/messages/?limit=40
    POST /api/chat/conversations/<pk>/messages/ {text} or {image}
    """
    conv = get_object_or_404(Conversation, pk=pk, participants=request.user)

    if request.method == "GET":
        limit = int(request.query_params.get("limit", 40))
        msgs = conv.messages.select_related("sender").order_by("-created")[:limit]
        data = [
            {
                "id": m.id,
                "sender": m.sender.username,
                "text": m.text or "",
                "image": m.image.url if m.image else None,
                "created": m.created,
                "is_own": m.sender_id == request.user.id,
            }
            for m in reversed(list(msgs))  # oldest→newest
        ]
        return Response(data)

    # POST
    text = (request.data.get("text") or "").strip()
    image = request.FILES.get("image")
    if not text and not image:
        return Response({"detail": "text or image required"}, status=400)

    m = Message.objects.create(conversation=conv, sender=request.user, text=text, image=image)
    data = {
        "id": m.id,
        "sender": m.sender.username,
        "text": m.text or "",
        "image": m.image.url if m.image else None,
        "created": m.created,
        "is_own": True,
    }
    return Response(data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_read(request, pk):
    # placeholder; you can implement real unread counters later
    get_object_or_404(Conversation, pk=pk, participants=request.user)
    return Response({"ok": True})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_conversation(request):
    """
    POST /api/chat/start/ {username}
    Creates (or retrieves) a 1:1 conversation and returns its id + other user.
    """
    username = (request.data.get("username") or "").strip()
    if not username:
        return Response({"detail": "username required"}, status=400)

    other = get_object_or_404(User, username__iexact=username)
    if other.id == request.user.id:
        return Response({"detail": "Cannot message yourself"}, status=400)

    conv = (
        Conversation.objects.filter(participants=request.user)
        .filter(participants=other)
        .first()
    )
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.set([request.user, other])

    return Response({"id": conv.id, "other": _simple_user(other)})
