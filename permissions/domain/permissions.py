from rest_framework.permissions import BasePermission, DjangoModelPermissions
from django.contrib.auth.models import Group
from rest_framework.request import Request
from users.domain.models import User
from permissions.domain.decorators.user_decorator import *
from permissions.domain.permission_utility.permissions_methods import *
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




#Class to verify if a user has permissions to access the users API (checks if has a user o group permission in any business asociated)
class permissionsToCheckUsers(DjangoModelPermissions):
    def has_permission(self, request:Request, view):
        user = request.user
      
        user_id = view.kwargs.get("user_id")
        business_id = view.kwargs.get("business_id")
        
        if not business_id:
          return False
        
        consulted_is_superuser = user_is_superadmin(user_id)
        permission_codename = get_permission_codename(view,request)
        user_clearance = type_of_user_access(user_id=user.id,business_id=business_id,permission=permission_codename)
        
        if not user_clearance:
          return False
        
        #auth to check a business users list
        if not user_id and user_clearance: 
          return True
               
        
        if consulted_is_superuser:
          if user_clearance == 'superuser':
             return True
          return False
        
        return user_clearance != None
          

class permissionsToCheckGroups(DjangoModelPermissions):
    def has_permission(self, request, view):

        user = request.user
        method = request.method
        
        if user.is_superuser:
          return True
        
        if method == 'GET' and user:
          return True

        return False


class permissionToCheckModel(DjangoModelPermissions):
    def has_permission(self, request, view):
        user = request.user
        business_id = view.kwargs.get("business_id")
        
        if not business_id:
          return False
        
        permission_codename = get_permission_codename(view,request)
        user_clearance = type_of_user_access(user_id=user.id,business_id=business_id,permission=permission_codename)
        
        if not user_clearance:
          return False
        
        return True
        
    
    
    


 

