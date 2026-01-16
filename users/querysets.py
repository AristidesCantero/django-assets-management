from django.db import models
from django.apps import apps


method_to_action = {
    'GET': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete'
}



class UserQuerySet(models.QuerySet):

    def users_allowed_for_user(self, request):
        user = request.user
        business_list = self.has_permission_over_users(user=user, request=request)
    

    def has_permission_over_users(self, request):
        user = request.user
        
        if user.is_superuser:
            Business = apps.get_model('locations', 'Business')
            businesses = Business.objects.all()
            return [b.id for b in businesses]
        
        if not user.is_authenticated or not user:
            return []
        
        permission_required = f'{method_to_action[request.method]}_{self._meta.model_name}'
        allowed_businesses = self.businesses_with_user_permission(user=user, perm_name=permission_required)
        return allowed_businesses
    



    def businesses_with_user_permission(self, user, request) -> list:
            
            permission_required = f'{method_to_action[request.method]}_{user._meta.model_name}'
            Permission = apps.get_model('auth', 'Permission')
            permission = Permission.objects.get(codename=permission_required)
            if not permission or not user.is_authenticated: 
                return []
            
            business_user_has_perm = self.get_business_where_user_has_permission(user=user, permission=permission)
            business_with_groups_user_belongs = self.get_business_groups_user_is(user=user)
            
            groups_not_allowed = []

            #searchs prohibitions for the groups the user belongs to / returns the permission ids
            if business_with_groups_user_belongs:
                groups_not_allowed = self.groups_forbidden_to_make_action_of_permission(permission=permission, bg_user_belongs=business_with_groups_user_belongs)

            allowed_businesses = []
            # remove businesses where the group has prohibition for the permission
            if groups_not_allowed:
                for b, g in business_with_groups_user_belongs:
                    if g not in groups_not_allowed:
                        allowed_businesses.append(b)

            # combine both lists without repeat / are the ids of the allowed businesses
            allowed_businesses = set(allowed_businesses + business_user_has_perm)

            return allowed_businesses
    

    def get_business_where_user_has_permission(self, user, permission) -> list:
        UserBusinessPermission = apps.get_model('permissions', 'UserBusinessPermission')
        ubp_query = "SELECT id, business_key_id FROM permissions_userbusinesspermission WHERE user_key_id = %s AND permission_id = %s AND active=true" % (user.id, permission.id)
        business_with_user_perm = [str(ubpm.business_key_id) for ubpm in UserBusinessPermission.objects.raw(ubp_query)]
        return business_with_user_perm


    def get_business_groups_user_is(self, user) -> set:
        GroupBusinessPermission = apps.get_model('permissions', 'GroupBusinessPermission')
        gbp_query = "SELECT id, group_key_id, business_key_id FROM permissions_groupbusinesspermission WHERE user_key_id = %s AND active=true" % user.id
        businesses_and_keys = set([(str(gbpm.business_key_id) ,str(gbpm.group_key_id)) for gbpm in GroupBusinessPermission.objects.raw(gbp_query)])
        return businesses_and_keys


    def groups_forbidden_to_make_action_of_permission(self, permission, bg_user_belongs: dict) -> list:
        Permission = apps.get_model('auth', 'Permission')
        gfp_groups = set([g[1] for g in bg_user_belongs])
        gfp_groups_not_allowed_query = "SELECT id, group_id FROM permissions_forbiddengrouppermissions WHERE group_id IN (%s) AND permission_id = %s" % (",".join(gfp_groups), permission.id)
        groups_not_allowed =[perm.group_id for perm in Permission.objects.raw(gfp_groups_not_allowed_query)]

        return groups_not_allowed