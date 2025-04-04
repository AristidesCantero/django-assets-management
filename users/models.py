from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords


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
    username = models.CharField(max_length = 255, unique=True)
    email = models.EmailField('Correo Electrónico' ,max_length=255 ,unique=True)
    name = models.CharField('Nombres', max_length=255, blank=True, null=True)
    last_name = models.CharField('Apellidos', max_length=255, blank=True, null=True)
    image = models.ImageField('Imagen de Perfil', upload_to='perfil/', max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    historical = HistoricalRecords()
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name', 'last_name']

    def __str__(self):
        return self.email
    
        
