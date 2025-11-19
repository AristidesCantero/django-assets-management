from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords
from locations.models import Business
from django.db.models import Model


# Create your models here.

class UserManager(BaseUserManager):
    def _create_user(self, username, email, name, last_name, password, is_staff, is_superuser, **extra_fields):
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name,
            last_name=last_name,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, username, email, name, last_name, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, False, False, **extra_fields)

    def create_superuser(self, username, email, name, last_name, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, True, True, **extra_fields)
    
class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length = 255, unique=True, null=False, blank=False, default='')
    email = models.EmailField('Correo Electrónico' ,max_length=255 ,unique=True, null=False, blank=False, default='')
    name = models.CharField('Nombres', max_length=255, blank=False, null=False, default='')
    last_name = models.CharField('Apellidos', max_length=255, blank=True, null=True, default='')
    image = models.ImageField('Imagen de Perfil', upload_to='perfil/', max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    historical = HistoricalRecords()
    objects = UserManager()
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name', 'last_name']

    def __str__(self):
        return self.email
    
    def get_business(self):
        return self.business_key
    
    def get_businesses(self):
        return Business.objects.filter(userbusinessmember__user_key=self.id)
    
    def get_plural(self):
        return 'users'

        
    
#permissions to do
# the user can have access to ubscribed businesses
# ver si se ha verificado que el usuario solo pueda acceder a negocios donde este inscrito (por comprobar)


# the users will have access to the locations where they are subscribed
#no implementado aun
 
# roles (grupos): superadmin, administrator, manager, user
#por definir capacidades


# permissions (permisos): add, change, delete, view
#por definir capacidades junto a roles

# check a way to allow admin and superadmin to determine what changes can a manager do
#establecer permisos de manager para que no pueda hacer todo lo que un admin pero que un admin pueda asignarle permisos a un manager

# what users can exists u¿in multiple businesses?

#what level of access a normal worker have? (view only?)
        
