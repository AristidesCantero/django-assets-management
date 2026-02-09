from rest_framework import serializers
from users.domain.models import User
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.presentation.api.validators import validate_name, validate_last_name, validate_email
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
        groups, permissions  = validated_data.get('groups', {}), validated_data.get('permissions', {})
        validated_data.pop('groups', None)
        validated_data.pop('permissions', None)

        return validated_data, groups, permissions
    


# Serializer only to create and search common users, defined for single user (not admin)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
    password = serializers.CharField(write_only=True, required=False)
    permissions = serializers.DictField(child=serializers.DictField(child = serializers.BooleanField()), required=False)
    groups = serializers.DictField(child=serializers.DictField(child = serializers.BooleanField()), required=False)
    
    
    def get_queryset(self, pk):
        user = User.objects.get(pk=pk)
        return user

    def update(self, instance, validated_data):
        validated_data, groups, permissions  = pop_non_user_fields(validated_data)
        updated_user = super().update(instance, validated_data)
        
        if permissions:
            set_user_businesses_and_permissions(user=updated_user, permissions=permissions)                
        if groups:
            set_user_groups(user=updated_user, groups=groups)

        if 'password' in validated_data:
            updated_user.set_password(validated_data['password'])
            updated_user.save()

        return updated_user
    
    def validate_permissions(self, perms):
        return validate_all_users_permissions(perms)
    
    def validate_groups(self, groups):
        return validate_all_users_groups(groups)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        
        return value


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
        
            if method in ['GET','PUT','PATCH']:
                context['permissions'] = get_user_businesses_permissions(user, json_format=json_format),
                context['groups'] = get_user_groups(user, json_format=json_format),
            return context


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    username = serializers.CharField(validators=[validate_name], required=True)
    name = serializers.CharField(validators=[validate_name], required=True)
    last_name = serializers.CharField(validators=[validate_last_name], required=True)
    email = serializers.EmailField(validators=[validate_email], required=True)
    password = serializers.CharField(write_only=True, required=True)
    permissions = serializers.DictField(child=serializers.DictField(child = serializers.BooleanField()), required=False)
    groups = serializers.DictField(child=serializers.DictField(child = serializers.BooleanField()), required=False)

    def get_queryset(self):
        queryset = self.Meta.model.objects.all()
        return queryset
    
    def create(self, validated_data):
        groups, permissions = validated_data.get('groups', {}), validated_data.get('permissions', {})
        validated_data.pop('groups', None)
        validated_data.pop('permissions', None)
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()

        if permissions:
            set_user_businesses_and_permissions(user=user, permissions=permissions)
        if groups:
           set_user_groups(user=user, groups=groups)
            
        return user
    
    def validate_permissions(self, perms):
        return validate_all_users_permissions(perms)              

    def validate_groups(self, groups):
        return validate_all_users_groups(groups)

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


                  