from django.db import models
from appcore.models import BaseModel

# Create your models here.

class Business(BaseModel):
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
    
class UserBusinessMember(BaseModel):
    user_key = models.ForeignKey('users.User', on_delete=models.CASCADE)
    business_key = models.ForeignKey(Business, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user_key.email} - {self.business_key.name} ({self.role})"
    
    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()
        return self
    
    def get_plural(self):
        return "userbusinessmembers"

class Headquarters(BaseModel):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    business_key = models.ForeignKey(Business, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    
    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()
        return self
    
    def get_plural(self):
        return "headquarters"
    
class InternalLocation(BaseModel):
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

