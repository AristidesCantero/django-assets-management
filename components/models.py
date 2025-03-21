from django.db import models
from business.models import *

# Create your models here.

class AssetSystem(models.Model):
    name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    asset_key = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Asset Systems'
        

class SubsystemComponent(models.Model):
    name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    asset_system_key = models.ForeignKey(AssetSystem, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Subsystem Components'
    

class MinimumComponent(models.Model):
    name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    subsystem_component_key = models.ForeignKey(SubsystemComponent, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Minimum Components'
