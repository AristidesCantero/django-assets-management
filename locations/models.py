from django.db import models

# Create your models here.

class Business(models.Model):
    name = models.CharField(max_length=100)
    tin = models.CharField(max_length=255)
    utr = models.CharField(max_length=255)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    
    def get_plural(self):
        return self.__class__.__name__.lower() + 'es'
    
    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()
        return self
    
class UserBusinessMember(models.Model):
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

class Headquarters(models.Model):
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
    
class InternalLocation(models.Model):
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

