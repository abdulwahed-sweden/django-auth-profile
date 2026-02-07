from rest_framework import viewsets, permissions
from django.contrib.auth.models import User

from .models import Profile
from .serializers import ProfileSerializer, UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.select_related('profile').all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
