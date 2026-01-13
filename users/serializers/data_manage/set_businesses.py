from users.models import User
from permissions.permissions import *
from django.contrib.auth.models import Group
from locations.models import Business




def set_user_business_permission(user: User, business: str, permission: str, action: bool):
    business = Business.objects.get(id=business)
    permission = Permission.objects.get(id=permission)
    ubp, created = UserBusinessPermission.objects.get_or_create(user_key=user,business_key=business,permission=permission)
    ubp.set_active(action) 
    
def set_group_business_permission(group: Group, business: Business, user: User, action: bool):
            gpb, created = GroupBusinessPermission.objects.get_or_create(group_key=group,business_key=business,user_key=user)
            gpb.set_active(action)

def set_user_businesses_and_permissions(user : User, permissions: dict[str,dict[str,bool]]):
            businesses_keys = permissions.keys()
            for business_key in businesses_keys:
                permission = permissions[business_key]
                for permission_key, is_marked in permission.items():
                    set_user_business_permission(user=user, business=business_key, permission=permission_key, action=is_marked)
                            
def set_user_groups(user: User, groups: dict[str,dict[str,bool]]):
        for business_key, group_instace in groups.items():
            business = Business.objects.get(id=business_key)
            for group_key, is_marked in group_instace.items():
                group = Group.objects.get(id=group_key)
                set_group_business_permission(group=group, business=business, user=user, action=is_marked)
               
