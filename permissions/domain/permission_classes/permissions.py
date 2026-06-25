from rest_framework.permissions import DjangoModelPermissions
from permissions.domain.decorators.user_decorator import *
from permissions.domain.permission_utility.permissions_methods import *
from locations.domain.models import Business
from permissions.domain.models import BusinessMembership


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


def user_has_level_over_user(valutated_user: User, consulted_user: User) -> bool:
    try:
      v_user_mship = BusinessMembership.objects.get(id=valutated_user.id)
      c_user_mrship = BusinessMembership.objects.get(id=consulted_user.id)
    except User.DoesNotExist:
      return False
    
    if v_user_mship.role.level > c_user_mrship.role.level:
      return True
    
    return False
    
    
def user_is_anonymous_or_empty(user):
  if not user or user.is_anonymous:
    return True
  return False
    

    
    
class permissionToInviteUsers(DjangoModelPermissions):
  """Method to check if user can invite another to a business\n check if user can add user then if has enough role level"""
  
  def has_permission(self, request, view):
        business_id = view.kwargs.get("business_id")
        user = request.user
        
        if user.is_superuser:
          return True
        
        permission_codename = 'add_user'
        
        user_has_perm = User.objects.user_has_clearance(user.id,business_id,permission_codename)
        try:
          user_membership = BusinessMembership.objects.get(user=user.id)
        except BusinessMembership.DoesNotExist:
          return False
          
        if not user_has_perm and not (user_membership.role.level>60):
          return False
        
        return True
        
     
class permissionsToCheckUser(DjangoModelPermissions):
    """Class to verify if a user has clearance to access a business user, it verifies: 
    \n 1. only superusers can only read superusers 
    \n 2. Consulted user and business exists 
    \n 3. User has clearance on business and over the user"""
    
    def has_permission(self, request, view):
        
        consulted_u_id = view.kwargs.get("user_id")
        business_id = view.kwargs.get("business_id")
        print(consulted_u_id)
        print(business_id)
        user = request.user
        consulted_user = User.objects.filter(id=consulted_u_id).first()
        business = Business.objects.filter(id=business_id).first()
        request.business = business
        
        non_existing_user = user_is_anonymous_or_empty(user)
        
        if non_existing_user:
          return False
        
        if not consulted_user or not business:
          return False
        #check superuser
        #business and consulted user (superuser only for superuser)
        #user business clearance
        if user.is_superuser:
            if consulted_user.is_superuser and request.method != "GET":
              return False
            return True
          
        if consulted_user.is_superuser:
          return False
        
        if not business or not consulted_user:
          return False

        permission_codename = get_permission_codename(view,request)
        if not permission_codename:
          return False
        
        user_has_perm = User.objects.user_has_clearance(user.id,business_id,permission_codename)
        if not user_has_perm:
          return False
        
        user_has_level = user_has_level_over_user(user, consulted_user)
        if not user_has_level and request.method != 'GET':
          return False
        
        return True
      

#expected for only apis that retrieves businesses data DO NOT access superusers or external businesses users with this permission
class permissionsToCheckUsers(DjangoModelPermissions):
    """Class to verify if a user has clearance to access a business user, it verifies: 
      \n 2. business exists 
      \n 3. User has clearance on business
      \n This permission is only for read purposes, any method external to GET will be forbidden"""
      
  
    def has_permission(self, request, view):
        
        if not request.method == 'GET':
          return False
        
        business_id = view.kwargs.get("business_id")
        user = request.user
        business = Business.objects.filter(id=business_id).first()
        request.business = business
        
        if user.is_superuser:
          return True
        
        if not business:
          return False

        permission_codename = get_permission_codename(view,request)
        if not permission_codename:
          return False
        
        user_has_perm = User.objects.user_has_clearance(user.id,business_id,permission_codename)
        if not user_has_perm:
          return False
        
        return True
          

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
        
        if user.is_superuser:
          return True
        
        if not business_id:
          return False
        
        permission_codename = get_permission_codename(view,request)
        user_clearance = User.objects.user_has_clearance(user.id,business_id,permission_codename)
        
        if not user_clearance:
          return False
        
        return True
        
    
class permissionOverBusinesses(DjangoModelPermissions):
  pass


class permissionOverBusiness(DjangoModelPermissions):
  pass

class permissionToCheckInternalLocation(DjangoModelPermissions):
  pass

class permissionToCheckHeadquarters(DjangoModelPermissions):
  pass

    


 

