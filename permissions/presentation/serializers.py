from rest_framework import serializers


from ..models import BusinessMembership, BusinessRole, UserBusinessPermission
from django.contrib.auth.models import Permission




class BusinessMembershipsSerializer(serializers.ModelSerializer):
    user_role_id = serializers.PrimaryKeyRelatedField(queryset=BusinessRole.objects.all(), required=False)
    permissions = serializers.DictField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = BusinessMembership
        fields = "__all__"
    
    def to_representation(self, instance):
        try:
          user_role = BusinessRole.objects.get(id=instance.role_id)
        except:
          user_role = None
          
        
        data = {
          "id": instance.id,
          "user": instance.user_id,
          "user_role": user_role.name if user_role else None,
          "joined_at": instance.joined_at,
        }
        data['user_permissions'] = UserBusinessPermission.objects.filter(membership=instance).values('permission', 'allowed')
        return data



class BusinessMembershipSerializer(serializers.ModelSerializer):
    user_role_id = serializers.PrimaryKeyRelatedField(queryset=BusinessRole.objects.all(), required=False)
    permissions = serializers.DictField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = BusinessMembership
        fields = "__all__"


    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions', {})
        instance.user_role_id = validated_data.get('user_role_id', instance.user_role_id)
        
        for perm_id, value in permissions_data.items():
            if value == 0:
                # Remove permission
                instance.permissions.filter(permission_id=perm_id).delete()
            elif value == 1:
                # Allow permission
                instance.permissions.create(permission_id=perm_id, allowed=True)
            elif value == 2:
                # Deny permission
                instance.permissions.create(permission_id=perm_id, allowed=False)
        
        instance.save()
        return instance
      
    def validate_user_role_id(self, value):
        business_id = self.context.get('business_id')
        if business_id is None:
            if value is not None and value.business_id is not None:
                raise serializers.ValidationError("The business_id is not provided, but the role is linked to a business.")
        else:
            if value is not None and value.business_id != business_id:
                raise serializers.ValidationError("The role's business_id does not match the provided business_id.")
        return value
      
    def validate_permissions(self, value):
        valid_permission_ids = set(Permission.objects.values_list('id', flat=True))
        #TO DO: change this method for intersections
        for perm_id, perm_value in value.items():
            if perm_id not in valid_permission_ids:
                raise serializers.ValidationError(f"Permission ID {perm_id} is invalid.")
            if perm_value not in [0, 1, 2]:
                raise serializers.ValidationError(f"Value {perm_value} is invalid for permission {perm_id}. Valid values are 0, 1, or 2.")
        return value
      
      
    def to_representation(self, instance):
        print(instance)
        try:
          user_role = BusinessRole.objects.get(id=instance.role_id)
        except:
          user_role = None
          
        
        data = {
          "id": instance.id,
          "user": instance.user_id,
          "user_role": user_role.name if user_role else None,
          "joined_at": instance.joined_at,
        }
        data['user_permissions'] = UserBusinessPermission.objects.filter(membership=instance).values('permission', 'allowed')
        return data
      
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
      
      
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'content_type', 'codename']

class GroupBusinessPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMembership
        fields = ['id', 'group', 'business', 'created_at', 'updated_at']
        

class GroupUserSerializer(serializers.Serializer):
    group_permissions = GroupBusinessPermissionSerializer(many=True)
    user_permissions = UserBusinessPermissionSerializer(many=True)





