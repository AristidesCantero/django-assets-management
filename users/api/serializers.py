from rest_framework import serializers
from users.models import User
from locations.models import Business
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.fields import ArrayField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from permissions.serializers import AdminPermissionSerializer
from permissions.models import AdminPermission
from rest_framework.validators import UniqueValidator, ValidationError, UniqueTogetherValidator
from users.api.validators import validate_name, validate_last_name, validate_email


DEFAULT_DJANGO_MODELS = [
    'users'
    'contenttypes',
    'sessions',
    'admin',
    'auth',
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        updated_user = super().update(instance, validated_data)
        if 'password' in validated_data:
            updated_user.set_password(validated_data['password'])
            updated_user.save()
        return updated_user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = User.objects.get(id=instance.id)
        #permissions = list(Permission.objects.all().values_list('codename','content_type', 'id'))
        contenttypes = list(ContentType.objects.exclude(model__in=DEFAULT_DJANGO_MODELS).values_list('app_label','model','id'))
        allPermissions = list(Permission.objects.all().values_list('codename','content_type', 'id'))
        contents = {}
        for contenttype in contenttypes:
            contents[contenttype[2]] = {'app_label':contenttype[0],'model':contenttype[1],'permissions':[]}

        for permission in allPermissions:
            contents[permission[1]]['permissions'].append([permission[0],permission[2]])


        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'name': instance.name,
            'last_name': instance.last_name,
            'image': instance.image.url if instance.image else None,
            'is_active': instance.is_active,
            'is_staff': instance.is_staff,
            'permissions': contenttypes
        }

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


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': instance['id'],
            'username': instance['username'],
            'email': instance['email']
        }


# Serializer to create and update admin users (only once)
class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
        
    name = serializers.CharField(validators=[validate_name])
    last_name = serializers.CharField(required=True,validators=[validate_last_name])
    email = serializers.EmailField(required=True,validators=[validate_email],)
    permission_type = ArrayField(serializers.ListField(required=True))
    business_key = serializers.PrimaryKeyRelatedField(
        queryset=Business.objects.all(),required=False, allow_null=True)

    permission_classes = [AdminPermissionSerializer]
    
    def get_queryset(self, pk):
        queryset = User.objects.get(pk=pk)
        adminPermission = AdminPermission.objects.filter(user_key=queryset.id).first()
        if not adminPermission.exists():
            return None
        return [queryset, adminPermission]



    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data)
            user.save()
            admin_permission_serializer = AdminPermissionSerializer(data={"user_key": user.id, "permission_type": validated_data.get('given_permissions', [])})
            if admin_permission_serializer.is_valid(raise_exception=True):
                admin_permission_serializer.save()
            else:
                user.delete()  # Rollback user creation if permissions are invalid
                raise ValidationError(admin_permission_serializer.errors)

            admin_permission_data = {"user_key": user.id, "permission_type": validated_data.get('permission_type', [])}

        except Exception as e:
            raise ValidationError(f"Error creating user: {str(e)}")
            
        return super().create(validated_data)
    

    def update(self, instance, validated_data):
        user = User.objects.get(id=instance.id)
        adminPermission = AdminPermission.objects.filter(user_key=instance.id).first()
        
        if not adminPermission:
            return serializers.ValidationError("This user dont have administrative role.")
            
        #actualiza la informacion del usuario
        updated_user = super().update(instance, validated_data)

        #guarda la info de adminPermission
        adminPermissionSerializer = AdminPermissionSerializer(adminPermission, 
                                                              data={"permission_type": validated_data.get('permissions', adminPermission.permission_type)}
                                                                ,partial=True)
        
        if not adminPermissionSerializer.is_valid():
            return serializers.ValidationError("Admin permission has invalid format.")

        if 'password' in validated_data:
            updated_user.set_password(validated_data['password'])

        adminPermissionSerializer.save()
        updated_user.save()
        return updated_user
    
    def validate_email(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        if User.objects.filter(username=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        
        return value
            


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'name': instance.name,
            'last_name': instance.last_name,
            'image': instance.image.url if instance.image else None,
            'is_active': instance.is_active,
            'is_staff': instance.is_staff,
            'permissions': AdminPermission.objects.filter(user_key=instance.id).first().permission_type
        }
        

# Serializer to list admin users with limited info
class UserAdminListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def get_queryset(self):
        users = self.Meta.model.objects.all()
        queryset = [user for user in users if AdminPermission.objects.filter(user_key=user.id).exists()]
        return queryset
    
    def to_representation(self, instance):
        permissions = AdminPermission.objects.filter(user_key=instance.id).first().permission_type
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'name': instance.name,
            'last_name': instance.last_name,
            'image': instance.image.url if instance.image else None,
            'is_active': instance.is_active,
            'is_staff': instance.is_staff,
            'permissions': permissions,
            'business_key': instance.business_key.id if instance.business_key else None
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
