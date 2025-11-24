from rest_framework.permissions import BasePermission,DjangoModelPermissionsOrAnonReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import User
from django.db.models import Model
from django.apps import apps
from permissions.models import AdminPermission, BusinessPermission, request_actions, AllPermissionChoices

#objective permissions
#-admin permission with limitations defined by another admin or the superadmin
#-manager permission with limitations defined by an admin
#-employee permission with limitations defined by an admin
#-guests permission with predefined limitations and cannot be changed


# model to make a special check if the business where the element belo
class permissionOverThisBusiness(BasePermission):
    def has_permission(self, request, view):
        method = request.method
        try:
            print("Checking business permissions for user id:", request.user.id)
            
            user = User.objects.get(id=request.user.id)
            
            businessPermission = BusinessPermission.objects.get(user_key=user.id)
            if not user.is_authenticated or not businessPermission:
                return False
            return True
        
        except User.DoesNotExist:
            print(f"No user has been identified")
            return False
        except BusinessPermission.DoesNotExist:
            print(f"User {user.name} does not have business permissions.")
            return False
        except:
            print("An error occurred while checking business permissions.")
            return False



class permissionsOverTheModel(DjangoModelPermissionsOrAnonReadOnly):
    """
    Similar to DjangoModelPermissions, but also includes object-level
    permissions.
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view)
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
    


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
class adminPermissionInModelsManager(isAdmin):

    def has_permission(self, request, view):
        return super().has_permission(request, view)    

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        try:
            app = apps.get_models()


            object_model = obj.__class__.__name__.lower()  # e.g., 'businesses'
            
            if object_model not in ['business','headquarter','asset','component','user'] or not object_model:
                return False
            
            method = request_actions[request.method]
            permission = method + "_" + object_model

            if permission not in AllPermissionChoices.permission_string():
                return False
            
            return True
            
        except:
            print("Could not determine the object's model name.")
            return False            



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
            