from django.db import models
from django.apps import apps


method_to_action = {
    'GET': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete'
}

def get_business():
  return apps.get_model('locations','Business')

def get_businessrole():
  return apps.get_model('permissions','BusinessRole')

def get_businessmembership():
  return apps.get_model('permissions', 'BusinessMembership')

def get_userbusinesspermission():
  return apps.get_model('permissions', 'UserBusinessPermission')

def get_model(app_label, model_name):
    return apps.get_model(app_label=app_label,model_name=model_name)

def get_permission_by_codename(app_label,model_name, codename):
    Permission = apps.get_model(app_label=app_label,model_name=model_name)
    return Permission.objects.get(codename=codename)

def query_where(conditional : dict[str:str]):
    if not conditional:
        return ""
    # Create a list of "key=value" strings from the dictionary
    conditions = [f"{key}={value}" for key, value in conditional.items()]
    
    # Join the conditions with " AND "
    return " AND ".join(conditions)
    
def select_query(fields:list[str], table_name, conditionals=""):
      return f"SELECT {", ".join(fields)} FROM {table_name}" + f" WHERE {conditionals}" if conditionals else ""

def extract_query_data(raw, query: str, row_names: list[str]):
  """Method focused in send a query through a raw SQL call method and retrieve the items in row_names"""
  raw_query = raw(query)
  return [{field: getattr(item, field,None) for field in row_names} for item in raw_query]



class UserQuerySet(models.QuerySet):
  

    def get_user_memberships(self, user_id) -> QuerySet:
      BusinessMembership = get_businessmembership()
      user_membership = BusinessMembership.objects.filter(user=user_id)
      return user_membership
  
  
    def get_user_membership(self, user_id, business_id) -> BusinessMembership | None:
      BusinessMembership = get_businessmembership()
      user_membership = BusinessMembership.objects.filter(user=user_id, business=business_id).first()
      return user_membership
    
    def get_userbusinessrole(self, user_id, business_id) -> BusinessRole | None :
      BusinessRole = get_businessrole()
      user_role = BusinessRole.objects.filter(business=business_id, user=user_id).first()
      return user_role
      
    
    def has_grouppermission(self, user_id, business_id, permission) -> bool:
      user_membership = self.get_user_membership(user_id, business_id)
      if not user_membership:
        return False
      
      user_business_role = user_membership.role
      user_grouppermissions = user_business_role.permissions
      
      if permission in user_grouppermissions:
        return True
      
      return False
      
      
    def has_userbusinesspermission(self, user_membership_id, permission_id):
       UserBusinessPermission = get_userbusinesspermission()
       user_permission = UserBusinessPermission.objects.filter(permission=permission_id,membership=user_membership_id).first()
       return user_permission
     
     
     
       
       
       
       
      
      
      
      

    
    #new 
    def get_permission(self, permission_name="", method="", accessed_model=""):
      required_permission = permission_name if permission_name else f'{method_to_action[method]}_{accessed_model}'
      Permission = apps.get_model('auth', 'Permission')
      permission = Permission.objects.filter(codename=required_permission).first()
      return permission




    

    