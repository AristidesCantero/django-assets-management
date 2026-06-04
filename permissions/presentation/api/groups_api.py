from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from permissions.presentation.serializers import GroupSerializer

class GroupListAPIView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all groups
        return Group.objects.all()
      
class GroupDetailAPIView(generics.RetrieveAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.all()