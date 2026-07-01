from rest_framework import serializers
from users.domain.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.presentation.serializers.data_manage.set_businesses import *
from users.presentation.serializers.data_manage.permission_manager import *
from users.presentation.serializers.validators.validators import *


DEFAULT_DJANGO_MODELS = [
    #"users",
    "contenttypes",
    "sessions",
    "admin",
    "auth",
]

DEFAULT_FORBIDDEN_MODELS = [
    'admin',
    'auth',
    'contenttypes',
    'sessions',
]



def pop_non_user_fields(validated_data: dict):
        businessmembership, userbusinesspermissions  = validated_data.get('businessmembership', {}), validated_data.get('userbusinesspermissions', {})
        validated_data.pop('businessmembership', None)
        validated_data.pop('userbusinesspermissions', None)

        return validated_data, businessmembership, userbusinesspermissions
    


# Serializer only to create and search common users, defined for single user (not admin)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
      
    
    password = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(required=False)
    
    
    def get_queryset(self, pk):
        user = User.objects.get(pk=pk)
        return user

    def update(self, instance, validated_data):
        updated_user = instance
        updated_user.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            updated_user.set_password(validated_data['password'])
          
        updated_user.save()

        return updated_user
    
  

    def soft_delete(self, instance, validated_data):
        if instance.is_superuser:
            raise serializers.ValidationError("Superadmins cannot be deactivated.")
        if BusinessMembership.objects.filter(user=instance, role__level=100).exists():
            raise serializers.ValidationError("Business owners cannot be deactivated.")
        instance.deactivate()
        return instance
    #create validations

    def to_representation(self, instance):
        request = self.context.get('request')
        method = request.method 

        if not instance:
            return {}
        
        # Representation of the use and all the permission this haves in the system
        user = User.objects.get(id=instance.id)
    
        context = {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'name': instance.name,
            'last_name': instance.last_name,
        }

        return self.representation(context, user, method, json_format=True)

    
    def representation(self, context, user: User, method: str, json_format=True):
        
            if False and method in ['GET','PUT','PATCH']:
                context['permissions'] = get_user_businesses_permissions(user, json_format=json_format),
                context['groups'] = get_user_groups(user, json_format=json_format),
            return context



class UserDeactivatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name','is_active']


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    username = serializers.CharField(validators=[validate_name], required=True)
    name = serializers.CharField(validators=[validate_name], required=True)
    last_name = serializers.CharField(validators=[validate_last_name], required=True)
    email = serializers.EmailField(validators=[validate_email_unique], required=True)
    password = serializers.CharField(write_only=True, required=True)



    def to_representation(self, instance):
        return {
                    'id': instance.id,
                    'username': instance.username,
                    'name': instance.name,
                    'last_name': instance.last_name,
                    'email': instance.email,
                    'permissions': get_user_businesses_permissions(instance),
                    'groups': get_user_groups(instance),
                }





# class created to add custom claims to the JWT token
class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['id'] = user.id
        # ...

        return token


                  