
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from users.querysets import UserQuerySet
from simple_history.models import HistoricalRecords
from users.querysets import UserQuerySet
from django.db import models, transaction
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
import hashlib
import secrets


def get_business_membership_model():
  return apps.get_model('permissions', 'BusinessMembership')

# Create your models here.

class UserManager(BaseUserManager.from_queryset(UserQuerySet)):

    #only high level logic, direct queries to database should use the UserQuerySet in get_queryset()    
    def user_has_clearance(self, user: User,business_id: str,permission_codename: str) -> bool:
      """this function returns if the user has a permission in a business"""
      
      #first we look for user membership
      user_membership = User.objects.get_user_membership(user, business_id)
      permission = Permission.objects.filter(codename=permission_codename).first()
      
      if not user_membership or not permission:
        return False
      
      #then with the user membership we can check the grouppermission and if neccesary personal permissions
      user_group_permission:bool = User.objects.has_grouppermission(user,permission.id)
      
      if user_group_permission:
        return True
      
      user_business_permission = User.objects.has_userbusinesspermission(user_membership, permission_codename)
      
      if user_business_permission:
        return user_business_permission.allowed
      
      return False

    #api
    def get_business_users(self, business_id: str) -> models.QuerySet[User]:
        """from a business id returns a queryset of User that belongs to the business"""
        business_users_ids = self.get_users_of_business(business_id)
        return User.objects.filter(id__in=business_users_ids, is_active=True)


    def get_user_if_in_business(self, business_id:str, user_id:str) -> User | None:
      business_membership = self.get_user_membership(user_id,business_id)
      return business_membership.user if business_membership else None

    def get_user_membership(self, user_id, business_id):
      """Returns the user membership for a given user and business"""
      BusinessMembership = get_business_membership_model()
      return BusinessMembership.objects.filter(user_id=user_id, business_id=business_id).first()


    def get_users_of_business(self, business_id):
      """from a business id returns a queryset of User that belongs to the business"""
      BusinessMembership = get_business_membership_model()
      
      business_users_ids = BusinessMembership.objects.filter(business_id=business_id).values_list('user_id', flat=True)
      return User.objects.filter(id__in=business_users_ids)


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
  
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="verification_tokens")

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
      
      


#invitation class only for existing users, change user for emails when moving to Saas models
class Invitation(models.Model):
    class Meta:
      unique_together = ("user","business")
  
    business = models.ForeignKey("locations.Business", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(hours=24))

    def __str__(self):
        return f"Invitation to {self.user} for {self.business}"
      
      
    @staticmethod
    def generate_token(user, business):
        raw_token = secrets.token_urlsafe(32)

        token_hash = hashlib.sha256(
            raw_token.encode()
        ).hexdigest()

        Invitation.objects.create(
            user=user,
            token=token_hash,
            business=business,
            expires_at=timezone.now() + timedelta(hours=24)
        )

        return raw_token
      
      
    def refresh_old_token(user):
      existing_token = Invitation.objects.filter(user_id=user.id).first()
      print(existing_token.expires_at)
      
      if not existing_token:
        return None
      
      #alternate
      #token_hash = make_password(raw_token)
      raw_token = secrets.token_urlsafe(32)
      token_hash = hashlib.sha256(
          raw_token.encode()
      ).hexdigest()
      
      existing_token.token = token_hash
      existing_token.expires_at = timezone.now() + timedelta(hours=24)
      existing_token.save()
      
      print(existing_token.expires_at)
      return raw_token