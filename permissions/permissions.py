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

def checkIfUserHasPermission(user: User, perm_name = str):
        permission = Permission.objects.get(codename=perm_name)
        if not permission or not user.is_authenticated: 
            return False
        
        #search if user has the permission in any business, saves the ids
        ubp_query = "SELECT * FROM permissions_userbusinesspermission WHERE user_key_id = %s AND permission_id = %s AND active=true" % (user.id, permission.id)
        ubp = [str(ubpm.id) for ubpm in UserBusinessPermission.objects.raw(ubp_query)]

        #searchs the groups where the user belongs
        gbp_query = "SELECT * FROM permissions_groupbusinesspermission WHERE user_key_id = %s AND active=true" % user.id
        gbp = [str(gbpm.group_key_id) for gbpm in GroupBusinessPermission.objects.raw(gbp_query)]
        
        gpfp_perm = []

       # if the user belongs to a group, search if the group has a prohibition over this permission
        if gbp:
            gpfp_perm =[perm.id for perm in Permission.objects.raw("SELECT * FROM permissions_forbiddengrouppermissions WHERE group_id IN (%s) AND permission_id = %s" % (",".join(gbp), permission.id))]

        if gpfp_perm:
             return False

        gbp_perm = []

        # if the user belongs to a group, searchs if the group has the permission
        if gbp:
            gbp_perm = [perm.id for perm in Permission.objects.raw("SELECT id FROM auth_group_permissions WHERE group_id IN (%s) AND permission_id = %s" % (",".join(gbp), permission.id))]

        has_gbp = True if gbp_perm else False
        has_ubp = True if ubp else False

        return has_gbp or has_ubp



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
        
        
        permission_required = f'{method_to_action[request.method]}_{User._meta.model_name}'
        return checkIfUserHasPermission(user=user, perm_name=permission_required)


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