# from django.conf import settings
# from django.db import models
# from django.utils import timezone

# User = settings.AUTH_USER_MODEL

# class Profile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="profile",
#     )
#     display_name = models.CharField(max_length=150, blank=True)
#     bio = models.TextField(blank=True)
#     # NEW
#     location = models.CharField(max_length=120, blank=True, default="")
#     # make file paths long enough (some filenames + subdirs > 100)
#     avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, max_length=255)
#     cover  = models.ImageField(upload_to="covers/",  blank=True, null=True, max_length=255)

#     created_at = models.DateTimeField(default=timezone.now, editable=False)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.display_name or self.user.username


# class Follow(models.Model):
#     """A follows B."""
#     follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
#     following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_set")
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ("follower", "following")

#     def __str__(self):
#         return f"{self.follower_id} -> {self.following_id}"

# profiles/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()  # <-- IMPORTANT

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, max_length=255)
    cover  = models.ImageField(upload_to="covers/",  blank=True, null=True, max_length=255)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.username


class Follow(models.Model):
    """
    One row = follower follows following.
    """
    follower  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
        ]

    def __str__(self):
        return f"{self.follower} -> {self.following}"
