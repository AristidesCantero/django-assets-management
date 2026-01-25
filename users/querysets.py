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

    def user_can_access_model(self, request, accessed_model) -> list:
        user = request.user
        if not user.is_authenticated or not user:
            return []
        
        required_permission = f'{method_to_action[request.method]}_{accessed_model._meta.model_name}'
        Permission = apps.get_model('auth', 'Permission')
        permission = Permission.objects.get(codename=required_permission)
        if not permission:
            return []

        business_which_user_belongs_to = self.businesses_which_access_user_belongs(user_id=user.id)
        if not business_which_user_belongs_to:
            return []
        
        businesses_where_user_has_permission = self.businesses_user_belongs_allowed_to_user(user_id=user.id, businesses=business_which_user_belongs_to, permission_id=permission.id)
        if not businesses_where_user_has_permission:
            return []
        
        return [user]



    def user_can_access_user(self, request, accessed_user_id: str) -> dict:
            user = request.user
            accessed_user = self.get(pk=accessed_user_id)
            #user not found
            if not accessed_user:
                return {"user": None, "exists": False}
            
            required_permission = f'{method_to_action[request.method]}_{user._meta.model_name}'
            Permission = apps.get_model('auth', 'Permission')
            permission = Permission.objects.get(codename=required_permission)

            if user.is_superuser:
                return {"user": accessed_user, "exists": True}

            #permission does not exists
            if not permission:
                return {"user": None, "exists": True}

            business_which_user_belongs = self.businesses_which_access_user_belongs(user_id=accessed_user_id)

            #no businesses where the accessed user belongs
            if not business_which_user_belongs:
                return {"user": None, "exists": True}
            
            businesses_where_user_has_permission = self.businesses_user_belongs_allowed_to_user(user_id=user.id, businesses=business_which_user_belongs, permission_id=permission.id)

            #no businesses where the user has permission over the accessed user
            if not businesses_where_user_has_permission:
                return {"user": None, "exists": True}
            

            return {"user": accessed_user, "exists": True}

        # Implement logic to determine if 'user' can access 'user_to_access'
            pass

    def businesses_which_access_user_belongs(self, user_id: str) -> list:
        query = "SELECT DISTINCT id, business_key_id FROM permissions_userbusinesspermission WHERE user_key_id = %s AND active=true" % user_id
        return [str(ubpm.business_key_id) for ubpm in self.raw(query)]

    def businesses_user_belongs_allowed_to_user(self, user_id: str, businesses: list, permission_id: str) -> list:
        query = "SELECT DISTINCT id, business_key_id FROM permissions_userbusinesspermission WHERE user_key_id = %s AND active=true AND permission_id = %s AND business_key_id IN (%s)" % (user_id, permission_id, ",".join(businesses))
        return [str(ubpm.business_key_id) for ubpm in self.raw(query)]




    def users_allowed_to_user(self, request) -> list:
        user = request.user
        business_list = self.businesses_allowed_to_user(request=request)


        if not business_list:
            return []
        
        return self.users_belonging_to_businesses(business_list=business_list)

    def users_belonging_to_businesses(self, business_list: list) -> list:
        if not business_list:
            return []
        
        query =  "SELECT * FROM users_user WHERE id IN (SELECT DISTINCT user_key_id FROM permissions_userbusinesspermission WHERE business_key_id IN (%s) AND active=true)" % ",".join(business_list)
        users = list(self.raw(query))
        return users

    def businesses_allowed_to_user(self, request):
        user = request.user
        
        if user.is_superuser:
            Business = apps.get_model('locations', 'Business')
            businesses = Business.objects.all()
            return [b.id for b in businesses]
        
        if not user.is_authenticated or not user:
            return []
        
        allowed_businesses = self.businesses_in_which_user_has_permission(user=user, request=request)
        return allowed_businesses
    
    def businesses_in_which_user_has_permission(self, user, request) -> list:
            
            permission_required = f'{method_to_action[request.method]}_{user._meta.model_name}'
            Permission = apps.get_model('auth', 'Permission')
            permission = Permission.objects.get(codename=permission_required)
            if not permission: 
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