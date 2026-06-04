
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist
from permissions.presentation.serializers import PermissionSerializer

class PermissionListAPIView(generics.ListAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all permissions
        return Permission.objects.all()

class PermissionDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.all()