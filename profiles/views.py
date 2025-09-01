# # from rest_framework.decorators import api_view, permission_classes, parser_classes
# # from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
# # from rest_framework.permissions import AllowAny, IsAuthenticated
# # from rest_framework.response import Response
# # from django.contrib.auth import get_user_model
# # from .models import Profile
# # from .serializers import ProfileSerializer

# # User = get_user_model()

# # @api_view(["GET"])
# # @permission_classes([AllowAny])
# # def by_username(request):
# #     username = (request.query_params.get("username") or "").strip()
# #     if not username:
# #         return Response({"error": "username required"}, status=400)
# #     try:
# #         user = User.objects.get(username__iexact=username)
# #         prof = Profile.objects.get(user=user)
# #     except (User.DoesNotExist, Profile.DoesNotExist):
# #         return Response({"error": "not found"}, status=404)
# #     return Response(ProfileSerializer(prof, context={"request": request}).data, status=200)

# # @api_view(["GET", "PATCH"])
# # @permission_classes([IsAuthenticated])
# # @parser_classes([JSONParser, MultiPartParser, FormParser])   # ← allow JSON & FormData
# # def me(request):
# #     prof, _ = Profile.objects.get_or_create(user=request.user)

# #     if request.method == "PATCH":
# #         # Accept both JSON and multipart (for avatar/cover)
# #         s = ProfileSerializer(prof, data=request.data, partial=True, context={"request": request})
# #         if s.is_valid():
# #             s.save()
# #             return Response(s.data, status=200)
# #         return Response(s.errors, status=400)

# #     return Response(ProfileSerializer(prof, context={"request": request}).data, status=200)
# # profiles/views.py
# from django.views.decorators.cache import never_cache
# from rest_framework.decorators import api_view, permission_classes, parser_classes
# from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from django.contrib.auth import get_user_model
# from .models import Profile,Follow
# from django.db import IntegrityError
# from .serializers import ProfileSerializer

# User = get_user_model()

# @never_cache
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def by_username(request):
#     username = (request.query_params.get("username") or "").strip()
#     if not username:
#         return Response({"error": "username required"}, status=400)
#     try:
#         user = User.objects.get(username__iexact=username)
#         prof = Profile.objects.get(user=user)
#     except (User.DoesNotExist, Profile.DoesNotExist):
#         return Response({"error": "not found"}, status=404)
#     return Response(ProfileSerializer(prof, context={"request": request}).data, status=200)

# @never_cache
# @api_view(["GET", "PATCH"])
# @permission_classes([IsAuthenticated])
# @parser_classes([JSONParser, MultiPartParser, FormParser])
# def me(request):
#     prof, _ = Profile.objects.get_or_create(user=request.user)

#     if request.method == "PATCH":
#         s = ProfileSerializer(prof, data=request.data, partial=True, context={"request": request})
#         if s.is_valid():
#             s.save()
#             return Response(s.data, status=200, headers={"Cache-Control": "no-store"})
#         return Response(s.errors, status=400)

#     return Response(
#         ProfileSerializer(prof, context={"request": request}).data,
#         status=200,
#         headers={"Cache-Control": "no-store"},
#     )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def follow_toggle(request):
#     """
#     Body: { "username": "<target>" }
#     If already following -> unfollow, else follow.
#     Returns { following: bool, followers_count: int, following_count: int }
#     """
#     username = (request.data.get("username") or "").strip()
#     if not username:
#         return Response({"detail": "username is required"}, status=400)

#     try:
#         target = User.objects.get(username__iexact=username)
#     except User.DoesNotExist:
#         return Response({"detail": "user not found"}, status=404)

#     if target.id == request.user.id:
#         return Response({"detail": "cannot follow yourself"}, status=400)

#     rel = Follow.objects.filter(follower=request.user, following=target)
#     if rel.exists():
#         rel.delete()
#         following = False
#     else:
#         try:
#             Follow.objects.create(follower=request.user, following=target)
#             following = True
#         except IntegrityError:
#             following = True  # race: already created

#     followers_count = Follow.objects.filter(following=target.id).count()
#     following_count = Follow.objects.filter(follower=target.id).count()

#     return Response({
#         "following": following,
#         "followers_count": followers_count,
#         "following_count": following_count,
#     }, status=200)

# # profiles/views.py
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def suggested(request):
#     qs = Profile.objects.exclude(user=request.user).order_by("-updated_at")[:5]
#     s = ProfileSerializer(qs, many=True, context={"request": request})
#     return Response(s.data, status=200)


# profiles/views.py
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Profile, Follow
from .serializers import ProfileSerializer

User = get_user_model()


@api_view(["GET"])
@permission_classes([AllowAny])
def by_username(request):
    username = (request.query_params.get("username") or "").strip()
    if not username:
        return Response({"error": "username required"}, status=400)
    try:
        user = User.objects.get(username__iexact=username)
        prof = Profile.objects.get(user=user)
    except (User.DoesNotExist, Profile.DoesNotExist):
        return Response({"error": "not found"}, status=404)
    return Response(ProfileSerializer(prof, context={"request": request}).data, status=200)




# --- list followers of a user ---
@api_view(["GET"])
@permission_classes([AllowAny])
def followers_list(request):
    username = (request.query_params.get("username") or "").strip()
    if not username:
        return Response({"error": "username required"}, status=400)
    try:
        target = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return Response({"error": "user not found"}, status=404)

    qs = (Profile.objects.select_related("user")
          .filter(user__in=Follow.objects.filter(following=target).values("follower")))
    data = ProfileSerializer(qs, many=True, context={"request": request}).data
    return Response(data, status=200)


# --- list who a user is following ---
@api_view(["GET"])
@permission_classes([AllowAny])
def following_list(request):
    username = (request.query_params.get("username") or "").strip()
    if not username:
        return Response({"error": "username required"}, status=400)
    try:
        target = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return Response({"error": "user not found"}, status=404)

    qs = (Profile.objects.select_related("user")
          .filter(user__in=Follow.objects.filter(follower=target).values("following")))
    data = ProfileSerializer(qs, many=True, context={"request": request}).data
    return Response(data, status=200)



@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def me(request):
    prof, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "PATCH":
        s = ProfileSerializer(prof, data=request.data, partial=True, context={"request": request})
        if s.is_valid():
            s.save()
            return Response(s.data, status=200)
        return Response(s.errors, status=400)

    return Response(ProfileSerializer(prof, context={"request": request}).data, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_toggle(request):
    """
    POST { "username": "<target>" }
    """
    username = (request.data.get("username") or "").strip()
    if not username:
        return Response({"error": "username required"}, status=400)

    try:
        target = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return Response({"error": "user not found"}, status=404)

    if target == request.user:
        return Response({"error": "cannot follow yourself"}, status=400)

    # toggle
    obj, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        obj.delete()
        following = False
    else:
        following = True

    return Response({
        "username": target.username,
        "following": following,
        "followers_count": Follow.objects.filter(following=target).count(),
    }, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def suggested(request):
    """
    Return a small list of other users to follow.
    Query params: ?limit=5
    """
    limit = int(request.query_params.get("limit") or 5)
    # exclude me and people I already follow
    already = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)
    qs = (Profile.objects
          .select_related("user")
          .exclude(user=request.user)
          .exclude(user_id__in=list(already))
          .order_by("-created_at")[:max(1, min(limit, 20))])

    data = ProfileSerializer(qs, many=True, context={"request": request}).data
    return Response(data, status=200)


@api_view(["GET"])
@permission_classes([AllowAny])
def search(request):
    """
    GET /api/profiles/search/?q=ali
    Returns a thin payload for quick header search.
    """
    q = (request.query_params.get("q") or "").strip()
    if not q:
        return Response([], status=200)
    qs = (Profile.objects.select_related("user")
          .filter(Q(user__username__icontains=q) | Q(display_name__icontains=q))
          .order_by("user__username")[:10])

    out = []
    for p in qs:
        out.append({
            "username": p.user.username,
            "name": p.display_name or p.user.username,
            "avatar": ProfileSerializer(p, context={"request": request}).data.get("avatar", ""),
        })
    return Response(out, status=200)
