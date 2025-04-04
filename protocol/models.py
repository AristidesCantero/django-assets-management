from django.db import models
from assets.models import *
# Create your models here.


class maintenanceRoutine(models.Model):
    asset_key = models.ForeignKey(Asset, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.asset_key.name + " - " + self.description
    
    def maintenance_steps(self):
        return routineStep.objects.filter(routine_key=self.id)



class routineStep(models.Model):
    routine_key = models.ForeignKey(maintenanceRoutine, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.routine_key.asset_key.name + " - " + self.routine_key.description + " - " + self.description
