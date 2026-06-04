from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from permissions.domain.models import BusinessMembership, UserBusinessPermission
from permissions.presentation.serializers import GroupUserSerializer

class GroupUserAPIView(generics.RetrieveAPIView):
    serializer_class = GroupUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return BusinessMembership.objects.filter(user_key_id=user_id).select_related('group', 'business')