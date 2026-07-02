from rest_framework import serializers


from ..models import BusinessMembership, BusinessRole, UserBusinessPermission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType




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
    role_id = serializers.PrimaryKeyRelatedField(queryset=BusinessRole.objects.all(), required=False)
    permissions = serializers.DictField(child=serializers.IntegerField(), required=False)
    

    class Meta:
        model = BusinessMembership
        fields = ["role_id", "is_active","permissions"]


    def soft_delete(self, instance, validated_data):
        instance.is_active = False
        instance.save()
        return instance

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions', {})
        business_role = validated_data.pop('role_id', instance.role_id)
        
        
        instance.role = business_role 
        if instance.role.level >= 100:
          raise serializers.ValidationError("Cannot change role for a owner level user.")
        
        for perm_id, value in permissions_data.items():
            user_permission = UserBusinessPermission.objects.filter(membership=instance, permission_id=perm_id).first()
            
            if value[0] == 0:
                # Remove permission
                if user_permission:
                    user_permission.delete()
            elif value[0] == 1:
                # Allow permission
                if user_permission:
                    user_permission.allowed = True
                    user_permission.save()
                else:
                    UserBusinessPermission.objects.create(permission_id=value[1].id, allowed=True,membership=instance)
            elif value[0] == 2:
                # Deny permission
                if user_permission:
                    user_permission.allowed = False
                    user_permission.save()
                else:
                    UserBusinessPermission.objects.create(permission_id=value[1].id, allowed=False,membership=instance)
        
        instance.save()
        return instance
      
    def validate_role_id(self, value):
        business_id = self.context.get('business_id')
        business_role = value
              
        if (business_role.business_id) and (business_role.business_id != business_id):
          raise serializers.ValidationError(f"Role ID {value} does not belong to this business.")
        
        return business_role
      
    def validate_permissions(self, value):
        permissions = Permission.objects.all()
        valid_permission_ids = set(permissions.values_list('id', flat=True))
        permissions_dict = {}


        invalid_permissions = set(int(k) for k in value.keys()) - valid_permission_ids
        if invalid_permissions:
            raise serializers.ValidationError(f"Invalid permission IDs: {', '.join(map(str, invalid_permissions))}")
        
        invalid_values = [k for k, v in value.items() if v not in [0, 1, 2]]
        if invalid_values:
            raise serializers.ValidationError(f"Invalid values for permissions: {', '.join(invalid_values)}")
          
        value_to_permissions_dict = {int(k): [v, permissions.filter(id=k).first()] for k, v in value.items()}
        
        return value_to_permissions_dict
      

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
        
    
    
      
class PermissionListSerializer(serializers.ModelSerializer):
  class Meta:
    model = Permission
    fields = ['id', 'name', 'content_type', 'codename']
  
  def group_by_content_type(self, data_list):
    content_types_queryset = ContentType.objects.all()
    grouped_data = {}
    for item in data_list:
        content_type = item['content_type']
        content_type_name = content_types_queryset.filter(id=content_type).first()
        if not content_type_name:
            continue
        
        content_type_name = content_type_name.model + '_' + content_type_name.app_label
        if content_type_name not in grouped_data:
            grouped_data[content_type_name] = []

        grouped_data[content_type_name].append(item)
    return grouped_data  
  
  
  def to_representation(self, instance):
        queryset_list = instance.values('id','name','content_type','codename')
        sorted_by_content = self.group_by_content_type(queryset_list)
        return sorted_by_content

class GroupBusinessPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMembership
        fields = ['id', 'group', 'business', 'created_at', 'updated_at']
        

class GroupUserSerializer(serializers.Serializer):
    group_permissions = GroupBusinessPermissionSerializer(many=True)
    user_permissions = UserBusinessPermissionSerializer(many=True)





