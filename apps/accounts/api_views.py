from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions, viewsets

from .models import Profile
from .permissions import IsOwnerOrReadOnly
from .serializers import ProfileSerializer, UserPublicSerializer, UserSerializer


@extend_schema_view(
    list=extend_schema(summary="List all profiles", tags=["Profiles"]),
    retrieve=extend_schema(summary="Retrieve a profile", tags=["Profiles"]),
    create=extend_schema(summary="Create a profile", tags=["Profiles"]),
    update=extend_schema(summary="Update a profile", tags=["Profiles"]),
    partial_update=extend_schema(summary="Partial update a profile", tags=["Profiles"]),
    destroy=extend_schema(summary="Delete a profile", tags=["Profiles"]),
)
class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles.

    Provides full CRUD operations on Profile objects.
    All endpoints require authentication (session or token).
    Write operations are restricted to the profile owner.
    """

    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__username", "location", "bio"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]


@extend_schema_view(
    list=extend_schema(summary="List all users", tags=["Users"]),
    retrieve=extend_schema(summary="Retrieve a user", tags=["Users"]),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for users (read-only).

    Provides list and detail views for registered users.
    Each user includes nested profile data.
    All endpoints require authentication.
    Admin users see email addresses; regular users do not.
    """

    queryset = User.objects.select_related("profile").all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "first_name", "last_name"]
    ordering_fields = ["date_joined", "username"]
    ordering = ["-date_joined"]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return UserSerializer
        return UserPublicSerializer
