from django.db import models
from appcore.models import BaseModel
from users.querysets import UserQuerySet

class BusinessManager(models.Manager):
   
  
    def get_queryset(self):
        return super().get_queryset()

    def get_business_memberships_for_user(self, user_id):
        """This method returns a user_membership queryset based in a user id"""
        
        user_memberships =  UserQuerySet().get_user_memberships(user_id=user_id)
        return user_memberships

    def get_businesses_for_user(self, user_id):
        """This method check the user_memberships, then return a list of the business ids in memberships
        
        Note: method still unchecked, the returned value could be wrong
        
        """
        memberships = self.get_business_memberships_for_user(user_id)
        print(memberships)
        return memberships.values_list('business', flat=True).distinct()


class HeadquartersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_headquarters_by_business(self, business_id):
        return self.filter(business_id=business_id)

    def get_headquarter_by_ids(self, business_id, headquarter_id):
        return self.filter(business_id=business_id, headquarter_id=headquarter_id)


class InternalLocationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_internal_locations_by_headquarter(self, headquarter_id):
        return self.filter(headquarter_id=headquarter_id)

    def get_internallocation_by_ids(self, headquarter_id, internallocation_id):
        return self.filter(headquarter_id=headquarter_id, internallocation_id=internallocation_id)



class Business(BaseModel):
    objects = BusinessManager()

    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    tin = models.CharField(max_length=255, unique=True, null=False, blank=False)
    utr = models.CharField(max_length=255, unique=True, null=False, blank=False)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    def get_business(self):
        return self

    def __str__(self):
        return self.name
    
    def get_plural(self):
        return self.__class__.__name__.lower() + 'es'
    
    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()
        return self
    
    

class Headquarters(BaseModel):
    
    class Meta:
        unique_together = ('business_key','name')
    
    
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    business_key = models.ForeignKey(Business, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    objects = HeadquartersManager()

    def __str__(self):
        return self.name
    
    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()
        return self
    
    def get_plural(self):
        return "headquarters"
    
    def get_business(self):
        return self.business_key
    
class InternalLocation(BaseModel):
    objects = InternalLocationManager()

    name = models.CharField(max_length=100)
    floor = models.CharField(max_length=50)
    room_number = models.CharField(max_length=50)
    headquarters_key = models.ForeignKey(Headquarters, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name + (' Piso: '+ self.floor) if self.floor else ""
    
    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()
        return self
    
    def get_plural(self):
        return "internallocations"
    
    def get_business(self):
        return self.headquarters_key.get_business()

