from django.db import models
from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from appcore.models import BaseModel
from locations.domain.models import Business
from django.contrib.auth.models import Permission
  
  




#role in a business (permis)
class BusinessRole(models.Model):
    class Scope(models.TextChoices):
        GLOBAL = "global"
        BUSINESS = "business"

    scope = models.CharField(max_length=20, choices=Scope.choices)
  
    business = models.ForeignKey(Business, on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=100)
    permissions = models.ManyToManyField(Permission)
    is_system = models.BooleanField(default=False) #pinpoint critical roles (system_role)
    level = models.IntegerField(default=1,validators=[MaxValueValidator(100), MinValueValidator(1)])
    
    class Meta:
      constraints = [
        models.UniqueConstraint(fields=['name','business'],name='unique_role_name'),
        models.UniqueConstraint(fields=['business', 'level'],name='unique_business_level')
      ]



#Class to save the 
class BusinessMembership(models.Model):
  
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    business = models.ForeignKey("locations.Business", on_delete=models.CASCADE)
    role = models.ForeignKey(BusinessRole,on_delete=models.PROTECT)
    is_owner = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "business")
        
    def set_active(self, action=True):
        self.is_active = action
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.role_id:
            self.role = BusinessRole.objects.get(
                is_system=True,
                code="member"
            )

        super().save(*args, **kwargs)
        

#Clas to manage the bussinesses the user can access
class UserBusinessPermission(BaseModel):
    class Meta:
        unique_together = ('membership', 'permission')
        
    membership = models.ForeignKey(BusinessMembership,on_delete=models.CASCADE,default=3)
    permission = models.ForeignKey(Permission,on_delete=models.CASCADE)
    allowed = models.BooleanField(default=True)



    def __str__(self):
        return f'User { self.user_key.username} permission {self.permission.codename} in {self.business_key.name}'
    
    



# Class to manage the group where the user belongs (the group will give the permissions)







