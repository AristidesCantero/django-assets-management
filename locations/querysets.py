from django.db import models
from django.apps import apps
from users.querysets import UserQuerySet

method_to_action = {
    'GET': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete'
}

class HeadquartersQuerySet(models.QuerySet):
    def get_user_headquarters(self, request) -> dict:
          businesses_allowed = UserQuerySet().businesses_allowed_to_user(request=request)
          headquarters_by_business = {}
          for business_id in businesses_allowed:
               headquarters_by_business[business_id] = self.get_headquarters_by_business(business_id=business_id)
          return headquarters_by_business

            


    def get_headquarters_by_business(self, business_id):
            #headquarters = self.filter(business_key_id=business_id) todavia no esta asociada al modelo de headquarters en managers
            Headquarters = apps.get_model("locations","Headquarters")
            headquarters = Headquarters.objects.filter(business_key_id=business_id)
            return headquarters
            


    def headquarter_user_has_permission(self, request, pk) -> dict:
        headquarter = self.get(pk=pk)
        user = request.user

        if not headquarter:
             return {"hq":None,"exists":False}

        if not user or not user.is_authenticated:
             return {"hq":None, "exists":True}
            
        
        if user.is_superuser:
             return {"hq":headquarter, "exists":True}
        
        business = headquarter.get_business()
        permission_required = f"{method_to_action[request.method]}_{self.model.model_name}"
        Permission = apps.get_model('auth', 'Permission')
        permission = Permission.objects.get(codename=permission_required)
        user_has_perm = UserQuerySet().user_has_perm_over_business(user=user,business=business,perm=permission)

        if not user_has_perm:
             return {"hq":None, "exists":True}
        
        return {"hq":headquarter, "exists":True}

    

