
from django.contrib.auth.models import AbstractUser, BaseUserManager
from users.querysets import UserQuerySet
from simple_history.models import HistoricalRecords
from users.querysets import UserQuerySet
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
import hashlib
import secrets



# Create your models here.

class UserManager(BaseUserManager.from_queryset(UserQuerySet)):

    #only high level logic, direct queries to database should use the UserQuerySet in get_queryset()

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    
    
    def user_has_clearance(self, user_id: str, business_id: str, permission_name: str) -> bool:
      permission = self.get_permission(permission_name)
      if not permission:
        return False
      user_permission = self.user_business_personal_permission(user_id,business_id,permission.id)
      return True if user_permission else False
    
        


    def user_belongs_to_a_group(self, user, group):
        query =  "SELECT id FROM permissions_groupbusinesspermission WHERE user_key_id = %s and group_key_id = %s" % (user.id, group.id)
        ubp = set([str(ubpm.id) for ubpm in self.raw(query)])
        return group.id in ubp



    def get_users_by_business(self, business_id: str):
        return User.objects.filter()



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
    
    def create_user_unregistered(self, username, email, name, last_name, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, False, False, **extra_fields)

    def create_superuser(self, username, email, name, last_name, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, True, True, **extra_fields)
    


class User(AbstractUser):
    username = models.CharField(max_length = 255, unique=True, null=False, blank=False, default='')
    email = models.EmailField('Correo Electrónico' ,max_length=255 ,unique=True, null=False, blank=False, default='')
    email_verified = models.BooleanField(default=False)
    name = models.CharField('Nombres', max_length=255, blank=False, null=False, default='')
    last_name = models.CharField('Apellidos', max_length=255, blank=True, null=True, default='')
    image = models.ImageField('Imagen de Perfil', upload_to='perfil/', max_length=255, blank=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
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
      
    def soft_delete(self):
      self.deleted_at = timezone.now()
      self.is_active = False
      self.save(update_fields=["deleted_at","is_active"])




class AuthProvider(models.Model):
    PROVIDERS = (
        ("password", "password"),
        ("google", "google"),
        ("github", "github"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="providers"
    )

    provider_type = models.CharField(max_length=20, choices=PROVIDERS)

    provider_uid = models.CharField(max_length=255)

    class Meta:
        unique_together = ("provider_type", "provider_uid")


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verification_tokens",unique=True
    )

    token_hash = models.CharField(max_length=64, unique=True)

    expires_at = models.DateTimeField()

    consumed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_token(user):
        raw_token = secrets.token_urlsafe(32)

        token_hash = hashlib.sha256(
            raw_token.encode()
        ).hexdigest()

        EmailVerificationToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=24)
        )

        return raw_token
      
    def refresh_old_token(user):
      existing_token = EmailVerificationToken.objects.filter(user_id=user.id).first()
      
      if not existing_token:
        return None
      
      #alternate
      #token_hash = make_password(raw_token)
      raw_token = secrets.token_urlsafe(32)
      token_hash = hashlib.sha256(
          raw_token.encode()
      ).hexdigest()
      
      existing_token.token_hash = token_hash
      existing_token.expires_at = timezone.now() + timedelta(hours=24)
      existing_token.save()
      
      return raw_token
      

    @staticmethod
    @transaction.atomic
    def verify_token(raw_token):
        token_hash = hashlib.sha256(
            raw_token.encode()
        ).hexdigest()

        token = (
            EmailVerificationToken.objects
            .select_for_update()
            .filter(token_hash=token_hash)
            .first()
        )

        if not token:
            return "invalid"

        if token.consumed_at:
            return "already_used"

        if token.expires_at < timezone.now():
            return "expired"

        token.consumed_at = timezone.now()
        token.save(update_fields=["consumed_at"])

        user = token.user

        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=["email_verified"])

        return "verified"