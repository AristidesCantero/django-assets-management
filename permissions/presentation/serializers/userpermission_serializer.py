from rest_framework import serializers
from permissions.domain.models import UserBusinessPermission

class UserBusinessPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBusinessPermission
        fields = ['id', 'user', 'business', 'permission', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.business = validated_data.get('business', instance.business)
        instance.permission = validated_data.get('permission', instance.permission)
        instance.save()
        return instance
      