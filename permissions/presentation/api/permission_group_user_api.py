
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Permission
from permissions.domain.models import BusinessMembership, UserBusinessPermission

from permissions.presentation.serializers import GroupUserSerializer
from rest_framework.permissions import IsAuthenticated


class PermissionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        List all permissions.
        """
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_id(self, request, pk):
        """
        Retrieve a specific permission by ID.
        """
        try:
            permission = Permission.objects.get(pk=pk)
            serializer = PermissionSerializer(permission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)


class GroupListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        List all groups.
        """
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_id(self, request, pk):
        """
        Retrieve a specific group by ID.
        """
        try:
            group = Group.objects.get(pk=pk)
            serializer = GroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)



class GroupUserAPIView(generics.RetrieveAPIView):
    serializer_class = GroupUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return BusinessMembership.objects.filter(user_key_id=user_id).select_related('group', 'business')
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        group_perms = BusinessMembership.objects.filter(user_key_id=user_id).select_related('group', 'business')
        user_perms = UserBusinessPermission.objects.filter(user_key_id=user_id).select_related('business', 'permission')

        data = {
            'group_permissions': GroupUserSerializer(group_perms, many=True).data,
            'user_permissions': GroupUserSerializer(user_perms, many=True).data,
        }

        return Response(data)
