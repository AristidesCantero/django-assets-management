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
    

class Headquarters(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    business_key = models.ForeignKey(Business, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    
class InternalLocation(models.Model):
    name = models.CharField(max_length=100)
    floor = models.CharField(max_length=50)
    room_number = models.CharField(max_length=50)
    headquarters_key = models.ForeignKey(Headquarters, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name