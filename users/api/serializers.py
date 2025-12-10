from rest_framework import serializers
from users.models import User
from locations.models import Business
from permissions.models import UserBusinessPermission, GroupBusinessPermission
from permissions.models import ForbiddenGroupPermissions
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.fields import ArrayField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator, ValidationError, UniqueTogetherValidator
from users.api.validators import validate_name, validate_last_name, validate_email


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


def user_manage_permission(user: User, business: str, permission: str, action: bool):
    ubp, created = UserBusinessPermission.objects.get_or_create(
        user_key=user,
        business_key=business,
        permission=permission
    )
    ubp.set_active(action) 
    


def set_user_permissions(user : User, permissions: dict[str,dict[str,bool]]):
            businesses_keys = permissions.keys()

            for business_key in businesses_keys:
                permisison = permissions[business_key]
                for permission_key, is_marked in permisison.items():
                    user_manage_permission(user=user, business=business_key, permission=permission_key, action=is_marked)
                

                

def set_user_groups(user: User, groups: dict[str,bool]):
          
          for group_field, is_marked in groups.items():
                try:
                    group = Group.objects.get(id=group_field)
                    if is_marked:
                        user.groups.add(group)
                    else:
                        user.groups.remove(group)
                except Group.DoesNotExist:
                    raise ValidationError(f"Group with id {group_field} does not exist.")
               


def set_group_permissions(group: Group, permissions: dict[str,dict[str,bool]]):
        for group_permission, is_marked in permissions.items():
                try:
                    permission = Permission.objects.get(id=group_permission)
                    if is_marked:
                        group.permissions.add(permission)
                except Permission.DoesNotExist:
                    raise ValidationError(f"Permission with id {group_permission} does not exist.")



def pop_non_user_fields(validated_data: dict):
        groups, permissions  = validated_data.get('groups', {}), validated_data.get('permissions', {})
        validated_data.pop('groups', None)
        validated_data.pop('permissions', None)

        return validated_data, groups, permissions
    
    



def handle_user_representation_contenttypes(user: User, contenttypes: list[tuple[str,str,int]], permissions: list[tuple[str,int,int]]):
    contents = {}

    for contenttype in contenttypes:
        contents[contenttype[2]] = {'app_label':contenttype[0],'model':contenttype[1],'permissions':[]}

    for permission in Permission.objects.all().values_list('codename','content_type','id'):
        if permission[1] in contents:
            contents[permission[1]]['permissions'].append([permission[0],permission[2],permission[2] in [x.id for x in user.user_permissions.all()]])

    return contents


# Serializer only to create and search common users, defined for single user (not admin)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
    password = serializers.CharField(write_only=True, required=False)
    permissions = serializers.DictField(child=serializers.BooleanField(), required=False)
    groups = serializers.DictField(child=serializers.BooleanField() , required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_queryset(self, pk):
        user = User.objects.get(pk=pk)
        return user

    
    def update(self, instance, validated_data):
        validated_data, groups, permissions  = pop_non_user_fields(validated_data)
        updated_user = super().update(instance, validated_data)
        
        if permissions:
            set_user_permissions(user=updated_user, permissions=permissions)                
        if groups:
            set_user_groups(user=updated_user, permissions=permissions)
        if 'password' in validated_data:
            updated_user.set_password(validated_data['password'])
            updated_user.save()

        return updated_user
    


    def to_representation(self, instance):
        request = self.context.get('request')
        method = request.method 

        # Representation of the use and all the permission this haves in the system
        user = User.objects.get(id=instance.id)
        contenttypes = [x for x in list(ContentType.objects.all().values_list('app_label','model','id')) if x[0] not in DEFAULT_DJANGO_MODELS]
        allPermissions = list(Permission.objects.all().exclude(codename__in=DEFAULT_FORBIDDEN_MODELS).values_list('codename','content_type','id'))
        userPermissions = [x.id for x in Permission.objects.filter(user=user)]

        context = {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'name': instance.name,
            'last_name': instance.last_name,
        }

        if not method in ['GET','PUT','PATCH']:
            return context
 
        contents = handle_user_representation_contenttypes(user=user, contenttypes=contenttypes, permissions=allPermissions)

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
    permissions = serializers.DictField(child=serializers.DictField(child = serializers.BooleanField()), required=False)
    groups = serializers.DictField(child=serializers.BooleanField() , required=False)


    def get_queryset(self):
        queryset = self.Meta.model.objects.all()
        return queryset
    

    def create(self, validated_data):
        validated_data, groups, permissions  = pop_non_user_fields(validated_data)
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()

        if permissions:
            set_user_permissions(user=user, permissions=permissions)
        if groups:
           set_user_groups(user=user, groups=groups)
            
        return user
    

    def validate_permissions(self, perms):
        validate_all_permissions(perms)              


    def validate_groups(self, groups):
        validate_all_groups(groups)

    def to_representation(self, instance):
        return {
                    'id': instance.id,
                    'username': instance.username,
                    'name': instance.name,
                    'last_name': instance.last_name,
                    'email': instance.email,
                    'permissions': ", ".join([str(perm.id) for perm in instance.user_permissions.all()]),
                    'groups': ", ".join([str(group.id) for group in instance.groups.all()]),
                }


            
    

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
        for group_permission, is_marked in value:
            try:
                Permission.objects.get(id=group_permission)
            except Permission.DoesNotExist:
                raise ValidationError(f"Permission with id {group_permission} does not exist.")  
        return value


    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'permissions': ", ".join([str(perm.id) for perm in instance.permissions.all()]),
            
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
        
        permissions = validated_data.get('permissions', {})
        validated_data.pop('permissions', None)
        updated_group = super().update(instance, validated_data)
            
        if permissions:
            set_group_permissions(group=updated_group, permissions=permissions)
                    
        return updated_group



    def validate_permissions(self, perms):
        group = self.instance

        if not group:
            # Si es creación, no hay permisos prohibidos definidos
            return perms

        forbidden = ForbiddenGroupPermissions.objects.filter(
            group=group
        ).values_list("permission_id", flat=True)

        forbidden_found = [p for p in perms if p.id in forbidden]

        if forbidden_found:
            names = ", ".join([p.codename for p in forbidden_found])
            raise serializers.ValidationError(
                f"Este grupo tiene prohibido asignarse los siguientes permisos: {names}"
            )

        return perms


    def to_representation(self, instance):
        return {
                    'id': instance.id,
                    'name': instance.name,
                    'permissions': [(perm.id, perm.name) for perm in instance.permissions.all()],
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





def validate_all_permissions(instance):
        permissions_businesses_keys = set(instance.keys())
        businesses_keys = set([str(business.id) for business in Business.objects.raw("SELECT id FROM locations_business")])
        invalid_keys = permissions_businesses_keys - businesses_keys

        if invalid_keys:
            raise ValidationError(f"Invalid business IDs: {', '.join(invalid_keys)}")
        
        all_invalid_p_keys = {}

        for key in permissions_businesses_keys:
            business_p = instance[key]
            permission_keys = set(business_p.keys())
            all_p_keys = set([str(perm.id) for perm in Permission.objects.raw("SELECT id FROM auth_permission")])
            invalid_p_keys = permission_keys - all_p_keys

            if invalid_p_keys:
                all_invalid_p_keys[key] = invalid_p_keys
        
        if all_invalid_p_keys:
            error_messages = []
            for business_id, invalid_perms in all_invalid_p_keys.items():
                error_messages.append(f"( Business id {business_id} : {', '.join(invalid_perms)} )")
            raise ValidationError('Invalid permission IDs found: ' + " ; ".join(error_messages))
        
        return instance

def validate_all_groups(instance):
        group_keys = set(instance.keys())
        all_group_keys = set([str(group.id) for group in Group.objects.raw("SELECT id FROM auth_group")])
        invalid_keys = group_keys - all_group_keys

        if invalid_keys:
            raise ValidationError(f"Invalid group IDs: {', '.join(invalid_keys)}")
        
        return instance