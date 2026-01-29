from django.db import models
from appcore.models import BaseModel
from assets.domain.models import *
# Create your models here.


class maintenanceRoutine(BaseModel):
    asset_key = models.ForeignKey(Asset, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.asset_key.name + " - " + self.description
    
    def maintenance_steps(self):
        return routineStep.objects.filter(routine_key=self.id)



class routineStep(BaseModel):
    routine_key = models.ForeignKey(maintenanceRoutine, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.routine_key.asset_key.name + " - " + self.routine_key.description + " - " + self.description
