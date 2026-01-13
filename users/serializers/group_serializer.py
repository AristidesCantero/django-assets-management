from rest_framework import serializers
from django.contrib.auth.models import Group
from rest_framework.validators import UniqueValidator
from users.serializers.data_manage.permission_manager import set_group_permissions
from users.serializers.validators.validators import validate_all_group_permissions






class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [UniqueValidator(queryset=Group.objects.all(), message="A group with that name already exists.")],
                     'required': True},
            'permissions': {'required': False},
        }

    permissions = serializers.DictField(child=serializers.BooleanField() , required=False)

    def get_queryset(self, key):
        group = Group.objects.get(id=key)
        return group

    def update(self, instance, validated_data):
        permissions = validated_data.get('permissions', {})
        validated_data.pop('permissions', None)
        updated_group = super().update(instance, validated_data)
            
        if permissions:
            set_group_permissions(group=updated_group, permissions=permissions)
                    
        return updated_group

    def validate_permissions(self, perms):
        return validate_all_group_permissions(perms)

    def to_representation(self, instance):
        return { 'id': instance.id, 'name': instance.name, 'permissions': [(perm.id, perm.name) for perm in instance.permissions.all()]}
    


    
class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [UniqueValidator(queryset=Group.objects.all(), message="A group with that name already exists.")],
                     'required': True},
            'permissions': {'required': False},
        }
    
    permissions = serializers.DictField(child=serializers.BooleanField() , required=False)

    def get_queryset(self):
        queryset = Group.objects.all()
        return queryset
    

    def create(self, validated_data):
            permissions = validated_data.get('permissions', {})
            validated_data.pop('permissions', None)
            group = super().create(validated_data)
        
            if permissions:
                set_group_permissions(group=group, permissions=permissions)
                    
            return group
    
    def validate_permissions(self, value):
        return validate_all_group_permissions(value)

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'permissions': ", ".join([str(perm.id) for perm in instance.permissions.all()]),
            
        }


