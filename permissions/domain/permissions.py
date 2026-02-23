from rest_framework.permissions import BasePermission, DjangoModelPermissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import Permission, Group
from users.domain.models import User
from permissions.domain.models import UserBusinessPermission, GroupBusinessPermission
from permissions.domain.decorators.user_decorator import *
from django.db.models import Model
from django.apps import apps

#objective permissions
#-admin permission with limitations defined by another admin or the superadmin
#-manager permission with limitations defined by an admin
#-employee permission with limitations defined by an admin
#-guests permission with predefined limitations and cannot be changed

method_to_action = {
    'GET': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete'
}

@returns_from_inner
def verify_unidentified_or_superadmin(request, consulted_user_id=None):
            user = request.user
            if not user.is_authenticated or not user:
                return False
            if user.is_superuser:
                consulted_user_is_superuser = User.objects.filter(id=consulted_user_id, is_superuser=True).first()
                if consulted_user_is_superuser and not request.method =='GET':
                        return False
                return True
            return None

def check_if_user_has_permission(request=None):
        if request is None:
            return False
        users_allowed = User.objects.users_allowed_to_user(request=request)
        return True if users_allowed else False

def checkIfUserHasPermissionOverModel(request=None, view=None):
    if request is None or view is None:
        return False
    
    user = request.user
    model_class = view.serializer_class.Meta.model if hasattr(view, 'serializer_class') else None

    #if hasattr(view, 'serializer_class'):
    #    model_class = view.serializer_class.Meta.model
    #else:
    #    model_class = None

    if not model_class:
        return False
    
    permission_required = f'{method_to_action[request.method]}_{model_class._meta.model_name}'
    
    users_allowed = User.objects.user_can_access_model(request=request, accessed_model=model_class)
    return True if users_allowed else False


def user_can_check_user(request, consulted_user_id: str) -> list[bool,bool]:
    user_value = User.objects.user_is_allowed_to_check_user(request=request, consulted_user_id=consulted_user_id)
    searched_user_exists = user_value.get("exists", False)
    user_value = user_value.get("user", None)  
    
    returned_list = [searched_user_exists, user_value]        
    return returned_list

def path_has_primary_key(path: str) -> bool:
    segments = path.strip('/').split('/')
    primary_key = segments[-1]
    return primary_key if primary_key.isdigit() else None

class isAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        group = Group.objects.get(name="ADMIN")
        groups_user_is_admin = User.objects.user_belongs_to_a_group(user=user,group=group)
        return True if groups_user_is_admin else False
    
class isManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        group = Group.objects.get(name="MANAGER")
        groups_user_is_manager = User.objects.user_belongs_to_a_group(user=user,group=group)
        return True if groups_user_is_manager else False



#Class to verify if a user has permissions to access the users API (checks if has a user o group permission in any business asociated)
class permissionsToCheckUsers(DjangoModelPermissions):
    @handle_early_return
    def has_permission(self, request, view):

        path_has_primary = path_has_primary_key(request.path)    
          
        if path_has_primary:
            verify_unidentified_or_superadmin(request,consulted_user_id=path_has_primary)
            exists, user_value = user_can_check_user(request=request, consulted_user_id=path_has_primary) 
                        
            if not user_value:
                return False
        
        verify_unidentified_or_superadmin(request)
            
        return check_if_user_has_permission(request=request)


class permissionsToCheckGroups(DjangoModelPermissions):
    def has_permission(self, request, view):
        verify_unidentified_or_superadmin(request)
        return False
        
        #permission_required = f'{method_to_action[request.method]}_{Group._meta.model_name}'
        #return checkIfUserHasPermission(user=user, perm_name=permission_required)


class permissionToCheckModel(DjangoModelPermissions):
    def has_permission(self, request, view):
        verify_unidentified_or_superadmin(request)
        return checkIfUserHasPermissionOverModel(request=request, view=view)