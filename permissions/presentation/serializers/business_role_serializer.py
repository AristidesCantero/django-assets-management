from permissions.domain.models import BusinessRole
from rest_framework import serializers
from django.contrib.auth.models import Permission
from rest_framework.validators import UniqueValidator
from permissions.domain.service.business_role_service import BusinessRoleService


permission_service = BusinessRoleService()


class BusinessRoleSerializer(serializers.ModelSerializer):
    """
    Requires the business id\n
    Serializer class to update, delete and read BusinessRole of a business\n
    restrictions: 
      name: between 3-50 alphanumeric characters, space allowed
      permissions: only permissions defined in django auth Permission
      level: Integer value between 1 to 100
    """
  
    class Meta:
        model = BusinessRole
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [UniqueValidator(queryset=BusinessRole.objects.all(), message="A role with that name already exists.")],
                     'required': True},
        }

    name = serializers.CharField(required=False)
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, required=False)
    level = serializers.IntegerField(max_value=100, min_value=1, required=False)


    def to_representation(self, instance):
        return { 'id': instance.id, 'name': instance.name, 'permissions': []}
    


    
class BusinessRoleListSerializer(serializers.ModelSerializer):
    """
    Requires the business id\n
    Serializer class to create BusinessRole instance and to read a list of BusinessRoles\n
    Fields: 
      name (required): between 3-50 alphanumeric characters, space allowed
      permissions: only permissions defined in django auth Permission
      level (required): Integer value between 1 to 100
    """
    
    class Meta:
        model = BusinessRole
        fields = '__all__'
    
        name = serializers.CharField(required=True)
        permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, required=False)
        level = serializers.IntegerField(max_value=100, min_value=1, required=True)

    def validate_name(self, instance):
      pass

    def to_representation(self, instance):
        return self.json_representation(instance)


    def json_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'permissions': {},
        }

