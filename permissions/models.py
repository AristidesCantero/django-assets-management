from django.db import models
from users.models import User
from appcore.models import BaseModel
from locations.models import Business
from django.contrib.auth.models import Group, Permission
from django.contrib.postgres.fields import ArrayField
from rest_framework_simplejwt.tokens import AccessToken
  
  


    
class ForbiddenGroupPermissions(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='forbidden_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)


    class Meta:
        unique_together = ('group', 'permission')

    def __str__(self):
        return f'Group { self.group.name} does not have permission to: {self.permission.codename}'



#Clas to manage the bussinesses the user can access
class UserBusinessPermission(BaseModel):
    user_key = models.ForeignKey(User, on_delete=models.CASCADE)
    business_key = models.ForeignKey(Business, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)


class GroupBusinessPermission(BaseModel):
    group_key = models.ForeignKey(Group, on_delete=models.CASCADE)
    business_key = models.ForeignKey(Business, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    







