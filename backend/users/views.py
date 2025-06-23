from django.shortcuts import render
from rest_framework import viewsets
from .models import User, UserProfile, SocialMediaAccount
from .serializers import UserSerializer, UserProfileSerializer, SocialMediaAccountSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    queryset = SocialMediaAccount.objects.all()
    serializer_class = SocialMediaAccountSerializer
    permission_classes = [IsAuthenticated]
