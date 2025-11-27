from rest_framework import serializers
from users.models import User
from locations.models import Business
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.fields import ArrayField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator, ValidationError, UniqueTogetherValidator
from users.api.validators import validate_name, validate_last_name, validate_email


DEFAULT_DJANGO_MODELS = [
    "users",
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


# Serializer only to create and search common users, defined for single user (not admin)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
    password = serializers.CharField(write_only=True, required=False)

    marked_fields = serializers.DictField(child=serializers.BooleanField(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        updated_user = super().update(instance, validated_data)

        if 'marked_fields' in validated_data:
            marked_fields = validated_data['marked_fields']
            
            for field, is_marked in marked_fields.items():
                try:
                    permission = Permission.objects.get(id=field)
                    if is_marked:
                        updated_user.user_permissions.add(permission)
                    else:
                        updated_user.user_permissions.remove(permission)
                except Permission.DoesNotExist:
                            raise ValidationError(f"Permission with id {field} does not exist.")  

        else:
            raise ValidationError(f"Permission with id {field} does not exist.")
                

        if 'password' in validated_data:
            updated_user.set_password(validated_data['password'])
            updated_user.save()
        return updated_user
    
    def to_representation(self, instance):
        request = self.context.get('request')
        method = request.method 

        # Representation of the use and all the permission this haves in the system
        user = User.objects.get(id=instance.id)
        #permisos = user.user_permissions.all()
        contenttypes = [x for x in list(ContentType.objects.all().values_list('app_label','model','id')) if x[0] not in DEFAULT_DJANGO_MODELS]
        allPermissions = list(Permission.objects.all().exclude(codename__in=DEFAULT_FORBIDDEN_MODELS).values_list('codename','content_type','id'))
        userPermissions = [x.id for x in Permission.objects.filter(user=user)]

        contents = {}

        for contenttype in contenttypes:
            contents[contenttype[2]] = {'app_label':contenttype[0],'model':contenttype[1],'permissions':[]}

        for permission in allPermissions:
            if permission[1] in contents:
                contents[permission[1]]['permissions'].append([permission[0],permission[2],permission[2] in userPermissions])

        context = {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'name': instance.name,
            'last_name': instance.last_name,
        }

        if method in ['GET','PUT','PATCH']:
            context['permissions'] = contents
        return context

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        
        return value
    

#Serializer to list users with limited info
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    username = serializers.CharField(validators=[validate_name], required=True)
    name = serializers.CharField(validators=[validate_name], required=True)
    last_name = serializers.CharField(validators=[validate_last_name], required=True)
    email = serializers.EmailField(validators=[validate_email], required=True)
    password = serializers.CharField(write_only=True, required=True)

    def get_queryset(self):
        queryset = self.Meta.model.objects.all()
        return queryset
    
    def representation(self, instance):
        return {
                    'id': instance.id,
                    'username': instance.username,
                    'name': instance.name,
                    'last_name': instance.last_name,
                    'email': instance.email,
                }


    def to_representation(self, instance):
        return self.representation(instance)


            
    

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
            is_permission = 'permissions' in validated_data
            validated_data.pop('permissions', None)
            group = super().create(validated_data)
            

            if is_permission:
                
                for group_permission, is_marked in permissions.items():
                    try:
                        permission = Permission.objects.get(id=group_permission)
                        if is_marked:
                            group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        raise ValidationError(f"Permission with id {group_permission} does not exist.")
                    
            return group


    def group_permissions_representation(self, instance):
        group = Group.objects.get(id=instance.id)
        permissions = group.permissions.filter()
    
    def validate_permissions(self, value):
        for group_permission, is_marked in value:
            try:
                Permission.objects.get(id=group_permission)
            except Permission.DoesNotExist:
                raise ValidationError(f"Permission with id {group_permission} does not exist.")  
        return value


    def to_representation(self, instance):
        group_permissions = self.group_permissions_representation(instance)
        return {
            'id': instance.id,
            'name': instance.name,
            'permissions': [(perm.id, perm.name) for perm in instance.permissions.all()],
        }



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [UniqueValidator(queryset=Group.objects.all(), message="A group with that name already exists.")],
                     'required': True},
            'permissions': {'required': False},
        }

    
    group_permissions = serializers.DictField(child=serializers.BooleanField() , required=False)

    def get_queryset(self, key):
        group = Group.objects.get(id=key)
        return group

    def update(self, instance, validated_data):
        updated_group = super().update(instance, validated_data)

        if 'group_permissions' in validated_data:
            group_permissions = validated_data['group_permissions']
            
            for group_permission, is_marked in group_permissions.items():
                try:
                    permission = Permission.objects.get(id=group_permission)
                    if is_marked:
                        updated_group.permissions.add(permission)
                    else:
                        updated_group.permissions.remove(permission)
                except Permission.DoesNotExist:
                            raise ValidationError(f"Permission with id {group_permission} does not exist.")  
        
        group_permissions = updated_group.permissions.all()

        return updated_group




    def representation(self, instance):
        return {
                    'id': instance.id,
                    'name': instance.name,
                    'permissions': [(perm.id, perm.name) for perm in instance.permissions.all()],
                }


    def to_representation(self, instance):
        return self.representation(instance)

# class created to add custom claims to the JWT token
class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['id'] = user.id
        # ...

        return token
