from rest_framework import serializers
from users.domain.models import User
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from permissions.domain.models import ForbiddenGroupPermissions


#the permissions, groups and users serializers are in users/api/serializers.py



class ForbiddenGroupPermissionsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForbiddenGroupPermissions
        fields = '__all__'
        
    permission = serializers.IntegerField()
    group = serializers.IntegerField()


    def create(self, validated_data):
        validated_data['permission'] = Permission.objects.get(id=validated_data['permission'])
        validated_data['group'] = Group.objects.get(id=validated_data['group'])
        
        return super().create(validated_data)
    
    def validate_group(self, value):
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError("El grupo con el ID proporcionado no existe.")
        
        return value
        
    
    def validate_permission(self, value):
        if not Permission.objects.filter(id=value).exists():
            raise serializers.ValidationError("El permiso con el ID proporcionado no existe.")
        
        return value

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'group': {
                'id': instance.group.id,
                'name': instance.group.name
            },  
            'permission': {
                'id': instance.permission.id,
                'codename': instance.permission.codename,
                'name': instance.permission.name
            }
        }



class ForbiddenGroupPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForbiddenGroupPermissions
        fields = '__all__'

    group = serializers.IntegerField()
    permission = serializers.IntegerField()

    def update(self, instance, validated_data):
        validated_data['permission'] = Permission.objects.get(id=validated_data['permission'])
        validated_data['group'] = Group.objects.get(id=validated_data['group'])

        return super().update(instance, validated_data) 
    
    
    def validate_group(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("Se debe retornar un ID de grupo válido.")
        
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError("El grupo con el ID proporcionado no existe.")
        
        return value
    
    def validate_permission(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("Se debe retornar un ID de permiso válido.")
        
        if not Permission.objects.filter(id=value).exists():
            raise serializers.ValidationError("El permiso con el ID proporcionado no existe.")
        
        return value
    

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'group': {
                'id'
                'name': instance.group.name
            },  
            'permission': {
                'codename': instance.permission.codename,
                'name': instance.permission.name
            }
        }