from users.domain.models import User
from permissions.domain.permissions import *
from django.contrib.auth.models import Group


def set_group_permissions(group: Group, permissions: dict[str,dict[str,bool]]):
        for group_permission, is_marked in permissions.items():
                permission = Permission.objects.get(id=group_permission)
                set_group_permission(group=group, permission=permission, action=is_marked)


def set_group_permission(group: Group, permission: Permission, action: bool):
        group.permissions.remove(permission) if not action else group.permissions.add(permission)

def get_user_businesses_permissions(user: User, json_format=True):
        user_business_perms = UserBusinessPermission.objects.raw("SELECT id, business_key_id, permission_id, active FROM permissions_userbusinesspermission WHERE user_key_id = %s", [user.id])
        businesses_permissions = {}

        for ubp in user_business_perms:
            is_active = ubp.active
            if ubp.business_key_id not in businesses_permissions:
                businesses_permissions[ubp.business_key_id] = {}

            nombre_permiso = ubp.permission_id if json_format else Permission.objects.get(id=ubp.permission_id).name        
            businesses_permissions[ubp.business_key_id][nombre_permiso] = is_active

        return businesses_permissions

def get_user_groups(user: User, json_format=True):
        user_groups = GroupBusinessPermission.objects.raw("SELECT id, business_key_id, group_key_id FROM permissions_groupbusinesspermission WHERE user_key_id = %s", [user.id])
        groups_dict = {}

        for group in user_groups:
            groups_dict[str(group.business_key_id)] = {}

            for group in user_groups:
                nombre_grupo = group.group_key_id if json_format else Group.objects.get(id=group.group_key_id).name
                groups_dict[str(group.business_key_id)][nombre_grupo] = group.active
             
        
        return groups_dict


