from django.db import models
from simple_history.models import HistoricalRecords



DEFAULT_SYSTEM_SEGREGATIONS = ["Electrico","Hidráulico","Neumático","Mecánico","Magnético"]

class SystemSegregation(models.Model):
    type = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

class Asset(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=255)
    family_model = models.CharField(max_length=255)
    part_number = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)
    op_capability = models.CharField(max_length=255)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    depth = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_energy_type = models.CharField(max_length=100, null=True, blank=True)
    technical_data = models.TextField()
    system_segregation = models.ForeignKey(SystemSegregation, null=True, on_delete=models.SET_NULL)
    additional_info = models.TextField()
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)


    def __str__(self):
        return self.name

 

