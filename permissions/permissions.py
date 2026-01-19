from rest_framework.permissions import BasePermission, DjangoModelPermissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import Permission, Group
from users.models import User
from permissions.models import UserBusinessPermission, GroupBusinessPermission
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


def belongsToAGroup(self, user: User, group: Group):
        query =  "SELECT id FROM permissions_groupbusinesspermission WHERE user_key_id = %s and group_key_id = %s" % (user.id, group.id)
        ubp = set([str(ubpm.id) for ubpm in GroupBusinessPermission.objects.raw(query)])
        return group.id in ubp

def checkIfUserHasPermission(request=None):
        if request is None:
            return False
        users_allowed = User.objects.users_allowed_to_user(request=request)
        return True if users_allowed else False

def check_if_user_can_check_user(request, accessed_user_id: str) -> bool:
    UserQuerySet = User.objects
    user_value = UserQuerySet.user_can_access_user(request=request, accessed_user_id=accessed_user_id)
    
    if not user_value:
         return []
   
    return user_value

def path_has_primary_key(path: str) -> bool:
    segments = path.strip('/').split('/')
    primary_key = segments[-1]
    return primary_key if primary_key.isdigit() else None

class isAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        group = Group.objects.get(name="ADMIN")
        groups_user_is_admin = belongsToAGroup(user=user,group=group)
        return True if groups_user_is_admin else False
    
class isManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        group = Group.objects.get(name="MANAGER")
        groups_user_is_manager = belongsToAGroup(user=user,group=group)
        return True if groups_user_is_manager else False

#Class to verify if a user has permissions to access the users API (checks if has a user o group permission in any business asociated)
class permissionsToCheckUsers(DjangoModelPermissions):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated or not user:
            return False
        
        if user.is_superuser:
            return True
        
        if path_has_primary_key(request.path):
            return check_if_user_can_check_user(request=request, accessed_user_id=path_has_primary_key(request.path))
        
        return checkIfUserHasPermission(request=request)


class permissionsToCheckGroups(DjangoModelPermissions):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not user:
            return False
        
        if user.is_superuser:
            return True
        
        return False
        
        #permission_required = f'{method_to_action[request.method]}_{Group._meta.model_name}'
        #return checkIfUserHasPermission(user=user, perm_name=permission_required)


class permissionToCheckModel(DjangoModelPermissions):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not user:
            return False
        
        if user.is_superuser:
            return True
        
        model_name = view.queryset.model._meta.model_name
        permission_required = f'{method_to_action[request.method]}_{model_name}'
        return checkIfUserHasPermission(user=user, perm_name=permission_required)