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


def get_userbusiness_permission_model():
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

def extract_query_data(model: type[models.Model], query: str, row_names: list[str]):
  raw_query = model.objects.raw(query)
  return [{field: getattr(item, field,None) for field in row_names} for item in raw_query]




class BusinessQuerySet(models.QuerySet):

    #conseguir listado de empresas en las que el usuario cuenta con permisos
    def user_allowed_businesses(user, request) -> list[int]:
        required_permission = f"{method_to_action[request.method]}_{Business._meta.model_name}"
        permission = get_permission_by_codename('auth', 'Permission', required_permission)
        businesses_allowed = UserQuerySet().get_business_where_user_has_userpermission(user=user, permission=permission)
        return businesses_allowed
    
    #check the businesses which the user has the permission for the model and based in the method


class UserQuerySet(models.QuerySet):
  
    def user_role_in_business(self, user_id: str,business_id: str) -> int | None:
      #check in groupbusinesspermission if user has a role in the business
      query_where = query_where({"business_key_id":business_id,"user_key_id":user_id,"active":"true"})
      gbp_query = select_query(["id", "group_key_id", "business_key_id"], "permissions_groupbusinesspermission", query_where)
      
      result = extract_query_data(self.raw, gbp_query,["group_key_id", "business_key_id"])
      role_id = result[result.keys()[0]] if result.keys() else 0
      
      return role_id
      
  
    def businesses_where_user_has_role(self, user_id) -> type[set(tuple[str,str])]:
      query_where = query_where({"user_key_id":user_id,"active":"true"})
      gbp_query = select_query(["id", "group_key_id", "business_key_id"], "permissions_groupbusinesspermission", query_where)

      return set(extract_query_data(self.raw, gbp_query, ["business_key_id", "group_key_id"]))      
          
    
    def user_business_personal_permission(self, user_id, business_id, permission_id) -> type[models.Model] | None:
      UserBusinessPermission = get_userbusiness_permission_model()
      return UserBusinessPermission.objects.filter(user_key = user_id, business_key= business_id, permission_id=permission_id)



    def get_permission(self, permission_name="", method="", accessed_model=""):
      required_permission = permission_name if permission_name else f'{method_to_action[method]}_{accessed_model}'
      Permission = apps.get_model('auth', 'Permission')
      permission = Permission.objects.filter(codename=required_permission).first()
      return permission




    

    