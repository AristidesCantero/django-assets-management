from rest_framework.permissions import BasePermission,DjangoModelPermissionsOrAnonReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import User
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

# model to make a special check if the business where the element belo
class permissionOverThisBusiness(BasePermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view)
        
    def has_object_permission(self, request, view, obj):
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



class permissionsOverTheModel(DjangoModelPermissionsOrAnonReadOnly):
    def has_permission(self, request, view):
        
         
        return super().has_permission(request, view)
    
    #determines if the user has the permission for modeel and method (ex: users.view_users)
    def has_object_permission(self, request, view, obj):

        

        user = request.user
        if not user.is_authenticated:
            return False
        
        method = request.method
        permission_required = f'{obj._meta.app_label}.{method_to_action[method]}_{obj._meta.model_name}'
        
        return user.has_perm(permission_required)

    


#access if the user is admin
class isAdmin(BasePermission):
    def has_permission(self, request, view):
        method = request.method
        try:
            user = User.objects.get(id=request.user.id)
            adminPermission = AdminPermission.objects.get(user_key=user.id)
            if not user.is_authenticated or not adminPermission:
                return False
    
            return True
        
        except User.DoesNotExist:
            print(f"User does not exists")
            return False
        except AdminPermission.DoesNotExist:
            print(f"User {user.name} does not have admin permissions.")
            return False
        except:
            print("An error occurred while checking admin permissions.")
            return False


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
            