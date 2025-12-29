from rest_framework.permissions import BasePermission, DjangoModelPermissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import Permission
from users.models import User
from permissions.models import UserBusinessPermission
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


def checkIfUserHasPermission(user: User, perm_name = str):
        permission = Permission.objects.get(codename=perm_name)
        if not permission: 
            return False
        
        query = "SELECT * FROM permissions_userbusinesspermission WHERE user_key_id = %s AND permission_id = %s AND active=true" % (user.id, permission.id)
        ubp = [str(ubpm.id) for ubpm in UserBusinessPermission.objects.raw(query)]

        return True if ubp else False







class isAdmin(BasePermission):
    def has_permission(self, request, view):
        return True









# model to make a special check if the business where the element belo
class permissionOverThisBusiness(BasePermission):
    def has_permission(self, request, view):
        return True
        print("goes in has permission")

        return super().has_permission(request, view)
        
    def has_object_permission(self, request, view, obj):
        return True
        print("goes in object permission")
        
        method = request.method
        try:
            user = User.objects.get(id=request.user.id)
            object_business = obj

            if not user.is_authenticated:
                return False
            
            return user.has_perm(f'{obj._meta.app_label}.{method_to_action[method]}_{obj._meta.model_name}', obj=object_business)
            return True
        
        except User.DoesNotExist:
            print(f"No user has been identified")
            return False
        except:
            print("An error occurred while checking business permissions.")
            return False





class permissionsToCheckUsers(DjangoModelPermissions):

    def has_permission(self, request, view):
            return True
    
    #determines if the user has the permission for modeel and method (ex: users.view_users)
    def has_object_permission(self, request, view, obj):

        user = request.user
        if not user.is_authenticated or not user:
            return False
        
        method = request.method
        model_name =f'{obj._meta.app_label}'
        permission_required = f'{method_to_action[method]}_{obj._meta.model_name}'

        
        return checkIfUserHasPermission(user=user, perm_name=permission_required)


    







#check in the 

class isManager(BasePermission):
    def has_permission(self, request, view):
        method = request.method
        user = User.objects.get(id=request.user.id)
        try:
            businessPermission = BusinessPermission.objects.get(user_key=user.id)
        except:
            print(f"User {user.email} does not have business permissions.")
            return False
        
        if not user.is_authenticated:
            return False
        
        return True



class managerPermissionInModelsManager(isManager):

    def has_permission(self, request, view):
        super().has_permission(request, view)


    def has_object_permission(self, request, view, obj):
        try:
            object_model = obj.get_plural().lower()  # e.g., 'businesses'
        except:
            print("Could not determine the object's model name.")
            return False

        super().has_permission(request, view)
        method = request.method
        businessPermission = BusinessPermission.objects.get(user_key=request.user.id)

        match method:
            case 'GET':
                return businessPermission.user_can("GET","businesses") #READ_USERS
            case 'POST':
                return businessPermission.user_can("POST","businesses") #CREATE_USERS
            case 'PUT' | 'PATCH':
                return businessPermission.user_can("PUT","businesses") #UPDATE_USERS
            case 'DELETE':
                return businessPermission.user_can("DELETE","businesses") #DELETE_USERS
            case _:
              return False



class isEmployee(BasePermission):
    def has_permission(self, request, view):
        method = request.method
        user = User.objects.get(id=request.user.id)
        try:
            businessPermission = BusinessPermission.objects.get(user_key=user.id)
        except:
            print(f"User {user.email} does not have business permissions.")
            return False
        
        if not user.is_authenticated:
            return False
        
        return True
    
    

class employeePermissionInModelsManager(isEmployee):
    def has_permission(self, request, view):
        super().has_permission(request, view)
    def has_object_permission(self, request, view, obj):
        try:
            object_model = obj.get_plural().lower()  # e.g., 'businesses'
        except:
            print("Could not determine the object's model name.")
            return False

        super().has_permission(request, view)
        method = request.method
        businessPermission = BusinessPermission.objects.get(user_key=request.user.id)

        match method:
            case 'GET':
                return businessPermission.user_can("GET","businesses") #READ_USERS
            case 'POST':
                return False #CREATE_USERS
            case 'PUT' | 'PATCH':
                return False #UPDATE_USERS
            case 'DELETE':
                return False #DELETE_USERS
            case _:
              return False
            