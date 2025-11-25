from django.db import models
from users.models import User
from appcore.models import BaseModel
from locations.models import Business
from django.contrib.postgres.fields import ArrayField
from rest_framework_simplejwt.tokens import AccessToken
  
  
all_choices = {'CREATE_USERS': 1}

class AllPermissionChoices(models.IntegerChoices):
    CREATE_USERS = 1, 'create_user',
    READ_USERS = 2, 'read_user',
    UPDATE_USERS = 3, 'update_user',
    DELETE_USERS = 4, 'delete_user',

    CREATE_BUSINESSES = 5, 'create_business',
    READ_BUSINESSES = 6, 'read_business',
    UPDATE_BUSINESSES = 7, 'update_business',
    DELETE_BUSINESSES = 8, 'delete_business',

    CREATE_HEADQUARTERS = 9, 'create_headquarter',
    READ_HEADQUARTERS = 10, 'read_headquarter',
    UPDATE_HEADQUARTERS = 11, 'update_headquarter',
    DELETE_HEADQUARTERS = 12, 'delete_headquarter',

    CREATE_ASSETS = 13, 'create_asset',
    READ_ASSETS = 14, 'read_asset',
    UPDATE_ASSETS = 15, 'update_asset',
    DELETE_ASSETS = 16, 'delete_asset',

    CREATE_COMPONENTS = 17, 'create_component',
    READ_COMPONENTS = 18, 'read_component',
    UPDATE_COMPONENTS = 19, 'update_component',
    DELETE_COMPONENTS = 20, 'delete_component',

    def permission_string():
        return [choice[1] for choice in AllPermissionChoices.choices]




request_actions = {'GET':'read','POST':'create','PUT':'update','PATCH':'update','DELETE':'delete'}
#admin is supposed to able all permissions
#but must fulfill the business permission to access a business

#the managers have limited permissions to able
manage_permission_choices = [
    AllPermissionChoices.READ_BUSINESSES,
    AllPermissionChoices.READ_HEADQUARTERS,
    AllPermissionChoices.READ_ASSETS,
    AllPermissionChoices.CREATE_ASSETS,
    AllPermissionChoices.READ_COMPONENTS,]



    
method_to_permission = {
            'GET': 'read_',
            'POST': 'create_',
            'PUT': 'update_',
            'PATCH': 'update_',
            'DELETE': 'delete_'}

    




#Clas to manage the bussinesses the user can access
class BusinessPermission(BaseModel):
    user_key = models.ForeignKey(User, on_delete=models.CASCADE)
    business_key = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='authorized_business')

    







