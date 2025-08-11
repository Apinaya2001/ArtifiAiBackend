
# from rest_framework import serializers
# from .models import Profile

# class ProfileSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source='user.username', read_only=True)
#     followers_count = serializers.IntegerField(source='followers.count', read_only=True)

#     class Meta:
#         model = Profile
#         fields = ('id','username','name','bio','avatar','cover','location','followers_count')



# # profiles/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name")

# class ProfileSerializer(serializers.ModelSerializer):
#     user = UserMiniSerializer(read_only=True)
#     username = serializers.CharField(source="user.username", read_only=True)

#     # return full URLs for images when request is in context
#     avatar = serializers.ImageField(use_url=True, required=False, allow_null=True)
#     cover  = serializers.ImageField(use_url=True, required=False, allow_null=True)

#     followers_count = serializers.IntegerField(source="followers.count", read_only=True)

#     class Meta:
#         model = Profile
#         fields = ("id", "user", "username", "name", "bio", "avatar", "cover",
#                   "location", "followers_count")
#         read_only_fields = ("id", "user", "username", "followers_count")
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id", "username", "name", "bio", "avatar", "cover",
            "location", "followers_count",
        ]
        read_only_fields = ["id", "username", "followers_count"]