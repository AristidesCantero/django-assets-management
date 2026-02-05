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


def get_user_headquarters(self, request) -> dict:
          businesses_allowed = UserQuerySet().businesses_allowed_to_user(request=request)
          headquarters_by_business = {}
          for business_id in businesses_allowed:
               headquarters_by_business[business_id] = self.get_headquarters_by_business(business_id=business_id)
          return headquarters_by_business





class HeadquartersQuerySet(models.QuerySet):
    def get_user_headquarters(self, request, dictionary=False) -> dict:
          businesses_allowed = UserQuerySet().businesses_allowed_to_user(request=request)
          headquarters_by_business = {}
          for business_id in businesses_allowed:
               headquarters_by_business[business_id] = self.get_headquarters_by_business(business_id=business_id, dictionary=dictionary)
          return headquarters_by_business

            


    def get_headquarters_by_business(self, business_id, dictionary=False):
            #headquarters = self.filter(business_key_id=business_id) todavia no esta asociada al modelo de headquarters en managers
            Headquarters = apps.get_model("locations","Headquarters")
            headquarters = Headquarters.objects.filter(business_key_id=business_id)
            if dictionary:
                  return {hq.pk : hq for hq in headquarters}
            return headquarters
            


    def headquarter_user_has_permission(self, request, pk) -> dict:
        Headquarters = apps.get_model('locations','Headquarters')
        headquarter = Headquarters.objects.get(pk=pk)
        user = request.user

        if not headquarter:
             return {"hq":None,"exists":False}

        if not user or not user.is_authenticated:
             return {"hq":None, "exists":True}
            
        
        if user.is_superuser:
             return {"hq":headquarter, "exists":True}
        
        business = headquarter.get_business()
        permission_required = f"{method_to_action[request.method]}_{Headquarters._meta.model_name}"
        Permission = apps.get_model('auth', 'Permission')
        permission = Permission.objects.get(codename=permission_required)
        user_has_perm = UserQuerySet().user_has_perm_over_business(user=user,business=business,perm=permission)

        if not user_has_perm:
             return {"hq":None, "exists":True}
        
        return {"hq":headquarter, "exists":True}

    



class InternalLocationQuerySet(models.QuerySet):
     
     def get_user_internal_locations(self, request):
          #return the hq in form { business_id: { headquarter.id : headquarter query}}
          elements_dict = HeadquartersQuerySet().get_user_headquarters(request=request, dictionary=True)

          for business_id in elements_dict.keys():
               hqs_ids = elements_dict[business_id]
               for hq_id in hqs_ids.keys():
                         headquarter = hqs_ids[hq_id]
                         internal_locations = self.get_internal_locations_by_headquarter(headquarter=headquarter)
                         hqs_ids[hq_id] = internal_locations
          
          return elements_dict
          
                     

                     
                     
                 
     def get_internal_locations_by_headquarter(self, headquarter, dictionary=False):
          #internal_location = self.filter(business_key_id=business_id) todavia no esta asociada al modelo de internal_location
          InternalLocation = apps.get_model("locations","InternalLocation")
          internal_locations = InternalLocation.objects.filter(headquarters_key=headquarter.id)
          if dictionary:
                return {int_loc.pk: int_loc for int_loc in internal_locations}
          return internal_locations




     def internal_location_if_user_has_perm(self, request, pk):
               #internal_location = self.get(pk=pk) todavia no esta asociada al modelo
               InternalLocation = apps.get_model("locations","InternalLocation")
               internal_location = InternalLocation.objects.filter(pk=pk).first()
               user = request.user

               if not internal_location:
                    return {"hq":None,"exists":False}

               if not user or not user.is_authenticated:
                    return {"hq":None, "exists":True}
                    
               
               if user.is_superuser:
                    return {"hq":internal_location, "exists":True}
               
               business = internal_location.get_business()
               permission_required = f"{method_to_action[request.method]}_{InternalLocation._meta.model_name}"
               Permission = apps.get_model('auth', 'Permission')
               permission = Permission.objects.get(codename=permission_required)
               user_has_perm = UserQuerySet().user_has_perm_over_business(user=user,business=business,perm=permission)

               if not user_has_perm:
                    return {"hq":None, "exists":True}
               
               return {"hq":internal_location, "exists":True}


