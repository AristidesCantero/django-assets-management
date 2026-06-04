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

businessmemberships = BusinessMembershipManager 


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
    businessmembership = serializers.IntegerField(required=False)
    userbusinesspermission = serializers.DictField(child=serializers.BooleanField(),required=False)
    
    
    def get_queryset(self, pk):
        user = User.objects.get(pk=pk)
        return user

    def update(self, instance, validated_data):
        validated_data, businessmembership, userbusinesspermission  = pop_non_user_fields(validated_data)
        updated_user = super().update(instance, validated_data)
        
        if businessmembership: #method to set businessmembership   
          businessmemberships.set_businessmembership(businessmembership)
                      
        if userbusinesspermission : #method to set the userbusinesspermission
          businessmemberships.set_userbusinesspermission(userbusinesspermission)

        if 'password' in validated_data:
            updated_user.set_password(validated_data['password'])
            updated_user.save()

        return updated_user
    
    #create validations
    def validate_businessmembership(instance):
      return validate_businessmembership(instance)
      
    def validate_userbusinesspermission(instance):
      return validate_userbusinesspermission(instance)
    
    def validate_email(self, value):
        return validate_email(value)


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


                  