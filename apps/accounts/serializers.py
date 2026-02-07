from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles.

    Returns profile details including bio, location, phone, and avatar URL.
    The `username` field is read-only and pulled from the related User model.
    """

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "username", "bio", "avatar_url", "location", "phone", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django's built-in User model (admin view).

    Includes nested profile data (read-only) alongside all standard user fields
    including email.
    """

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile"]


class UserPublicSerializer(serializers.ModelSerializer):
    """Serializer for non-admin users — hides email for privacy."""

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "profile"]
