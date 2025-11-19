from rest_framework import serializers
from users.models import User
from permissions.models import AdminPermission, ManagerPermission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPermission
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': instance.id,
            'user_key': instance.user_key.id,
            'permission_type': instance.permission_type,
        }
    
class PermissionListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AdminPermission
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': instance.id,
            'user_key': instance.user_key.id,
            'permission_type': instance.permission_type,
        }
    

class AdminPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPermission
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'user_key': instance.user_key.id,
            'permission_type': instance.permission_type,
        }


class AdminPermissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPermission
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': instance.id,
            'user_key': instance.user_key.id,
            'permission_type': instance.permission_type,
        }