from django.db import models
from django.apps import apps
from locations.models import Business


method_to_action = {
    'GET': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete'
}

class BusinessQuerySet(models.QuerySet):

    #conseguir listado de empresas en las que el usuario cuenta con permisos
    def user_allowed_businesses(user, request):
        required_permission = f"{method_to_action[request.method]}_{Business._meta.model_name}"
        Permission = apps.get_model('auth', 'Permission')
        permission = Permission.objects.get(codename=required_permission)
        businesses_allowed = UserQuerySet().get_business_where_user_has_userpermission(user=user, permission=permission)
        return businesses_allowed
    
    
    # 


    #check the businesses which the user has the permission for the model and based in the method



class UserQuerySet(models.QuerySet):

    # only direct queries to database, these queries are later used in manager

    def businesses_where_user_has_userpermission(self, user, business, perm):
        if not user or not business or not perm:
            return False

        UserBusinessPermission = apps.get_model('permissions', 'UserBusinessPermission')
        perm_exists = UserBusinessPermission.objects.filter(user_key_id = user.id, permission_id = perm.id, business_key_id = business.id).exists()
        return perm_exists

    def businesses_where_user_belongs(self, user_id: str) -> list:
        query = "SELECT DISTINCT id, business_key_id FROM permissions_userbusinesspermission WHERE user_key_id = %s AND active=true" % user_id
        query2 = "SELECT DISTINCT id, business_key_id FROM permissions_groupbusinesspermission WHERE user_key_id = %s AND active=true" % user_id
        list1 = [str(ubpm.business_key_id) for ubpm in self.raw(query)]
        list2 = [str(ubpm.business_key_id) for ubpm in self.raw(query2)]

        return list(set(list1+list2))

    def users_of_businesses_where_user_belongs(self, user_id: str, businesses: list, permission_id: str) -> list:
        query = "SELECT DISTINCT id, business_key_id FROM permissions_userbusinesspermission WHERE user_key_id = %s AND active=true AND permission_id = %s AND business_key_id IN (%s)" % (user_id, permission_id, ",".join(businesses))
        return [str(ubpm.business_key_id) for ubpm in self.raw(query)]




    

    def users_that_belongs_to_a_business(self, business_list: list) -> list:
        if not business_list:
            return []   
        
        query =  "SELECT * FROM users_user WHERE id IN (SELECT DISTINCT user_key_id FROM permissions_userbusinesspermission WHERE business_key_id IN (%s) AND active=true)" % ",".join(list(map(str,business_list)))
        users = list(self.raw(query))
        return users

    def get_business_where_user_has_userpermission(self, user, permission) -> list:
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