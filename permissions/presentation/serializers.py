from rest_framework import serializers




from django.contrib.auth.models import Permission, Group
from permissions.domain.models import BusinessMembership, UserBusinessPermission







class PermissionSerializer(serializers.ModelSerializer):
    class Meta:











































        model = Permission
        fields = ['id', 'name', 'content_type', 'codename']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


class GroupBusinessPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMembership
        fields = ['id', 'group', 'business', 'created_at', 'updated_at']


class UserBusinessPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBusinessPermission
        fields = ['id', 'user', 'business', 'permission', 'created_at', 'updated_at']


class GroupUserSerializer(serializers.Serializer):
    group_permissions = GroupBusinessPermissionSerializer(many=True)
    user_permissions = UserBusinessPermissionSerializer(many=True)


#the permissions, groups and users serializers are in users/api/serializers.py
