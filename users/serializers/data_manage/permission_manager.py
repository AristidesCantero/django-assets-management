from users.models import User
from permissions.permissions import *
from django.contrib.auth.models import Group


def set_group_permissions(group: Group, permissions: dict[str,dict[str,bool]]):
        for group_permission, is_marked in permissions.items():
                permission = Permission.objects.get(id=group_permission)
                set_group_permission(group=group, permission=permission, action=is_marked)


def set_group_permission(group: Group, permission: Permission, action: bool):
        group.permissions.remove(permission) if not action else group.permissions.add(permission)

def get_user_businesses_permissions(user: User):
        user_business_perms = UserBusinessPermission.objects.raw("SELECT id, business_key_id, permission_id FROM permissions_userbusinesspermission WHERE user_key_id = %s", [user.id])
        businesses_permissions = {}

        for ubp in user_business_perms:
            is_active = ubp.active
            if ubp.business_key_id not in businesses_permissions:
                businesses_permissions[ubp.business_key_id] = {}
            
            businesses_permissions[ubp.business_key_id][ubp.permission_id] = is_active
             
        return businesses_permissions

def get_user_groups(user: User):
        user_groups = GroupBusinessPermission.objects.raw("SELECT id, business_key_id, group_key_id FROM permissions_groupbusinesspermission WHERE user_key_id = %s", [user.id])
        groups_dict = {}

        for group in user_groups:
            groups_dict[str(group.business_key_id)] = {}

            for group in user_groups:
                groups_dict[str(group.business_key_id)][str(group.group_key_id)] = group.active
             
        
        return groups_dict


