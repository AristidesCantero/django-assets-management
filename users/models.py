from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords
from users.querysets import UserQuerySet


# Create your models here.

class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    def _create_user(self, username, email, name, last_name, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have email address')

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
    
    def user_has_permission_users(self, user, request):
        return UserQuerySet.businesses_with_user_permission(user, request)

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
    date_joined = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    historical = HistoricalRecords()
    objects = UserManager()
   
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name', 'last_name']

    def __str__(self):
        return self.name + ' ' + self.last_name
    
    def get_plural(self):
        return 'users'



