from users.domain.models import User
from permissions.domain.decorators.user_decorator import *


method_to_action = {
    'GET': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete'
}



def user_is_superadmin(user_id:str) -> User:
    return User.objects.filter(pk=user_id,is_superuser=True,is_active=True)
    

def user_has_permission(user_id:str, business_id:str, permission_name) -> bool:
    if not isinstance(user_id, int):
      raise ValueError(f"user id expected to be a number recieved {type(user_id)}")
    if not isinstance(business_id, int):
      raise ValueError(f"business id expected to be a number recieved {type(user_id)}")
    
    #TO DO method
    role_id = User.objects.user_role_in_business(user_id, business_id)
    if not role_id:
      return False
    
    #TO DO method
    user_is_allowed = User.objects.user_has_clearance(user_id, business_id, permission_name)
    
    return user_is_allowed
    
  
def type_of_user_access(user_id: str | User,business_id: str,permission:str) -> str | None:
    """
    Method to return if the user has clearance as superadmin, regular access (is allowed) or None if forbidden
    
    Parameters:
    user_id : id of the authenticated user
    business_id : id of the business of interest
    permission : codename of the permission, expected to be an auth_permission existing codename
    
    returns:
    a string with the access type of the user "superuser", "regular" or None
    """
  
    if not isinstance(user_id,(User,int,str)):
      print(f"user value expected to be User, str or int, recieved {type(user_id)}")
      return None

    user = user_id if isinstance(user_id,User) else User.objects.filter(id=user_id).first()
    
    if not user:
      return None

    if user_id.is_superuser:
      return 'superuser' 
      
    
    user_has_access = user_has_permission(user.id, business_id, permission)
    if user_has_access:
      return 'regular'
    
    return None
        
      
def get_permission_codename(view,request):
    model_class = view.serializer_class.Meta.model if hasattr(view, 'serializer_class') else None
    if not model_class:
        raise AttributeError("model_class expected to have value, view serialzier has empty Meta model")
    method = request.method
    if not method:
      raise AttributeError("Request method not found")
    
    action = method_to_action[request.method]
    return f"{action}_{model_class._meta.model_name}"   
        
      

