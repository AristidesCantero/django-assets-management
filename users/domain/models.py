from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords
from users.querysets import UserQuerySet, method_to_action
from django.apps import apps
from users.querysets import UserQuerySet

# Create your models here.

class UserManager(BaseUserManager.from_queryset(UserQuerySet)):

    #only high level logic, direct queries to database should use the UserQuerySet in get_queryset()

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    
    def user_has_permission_users(self, user, request):
        return self.get_queryset().businesses_with_user_permission(user, request)
    
    def get_user(self, request):
        user = request.user
        if not user.is_authenticated or not user:
            return None
        return user
        
    def get_permission(self, method, accessed_model):
        required_permission = f'{method_to_action[method]}_{accessed_model._meta.model_name}'
        Permission = apps.get_model('auth', 'Permission')
        permission = Permission.objects.get(codename=required_permission)
        return permission

    def user_belongs_to_a_group(self, user, group):
        query =  "SELECT id FROM permissions_groupbusinesspermission WHERE user_key_id = %s and group_key_id = %s" % (user.id, group.id)
        ubp = set([str(ubpm.id) for ubpm in self.raw(query)])
        return group.id in ubp

    def user_can_access_model(self, request, accessed_model):
        user = self.get_user(request)
        if not user:
            return []
        
        if user.is_superuser:
            return [user]

        permission = self.get_permission(method=request.method, accessed_model=accessed_model._meta.model_name)
        business_where_user_belongs = self.get_queryset().businesses_where_user_belongs(user_id=user.id)

        if not business_where_user_belongs or not permission:
            return []
        
        businesses_where_user_has_permission = self.users_of_businesses_where_user_belongs(user_id=user.id, businesses=business_where_user_belongs, permission_id=permission.id)
        if not businesses_where_user_has_permission:
            return []
        
        return [user]

    def user_is_allowed_to_check_user(self, request, accessed_user_id: str):
            user = request.user
            accessed_user = self.get(pk=accessed_user_id)
            
            if not accessed_user:
                return {"user": None, "exists": False}

            if user.is_superuser:
                return {"user": accessed_user, "exists": True}
            
            permission = self.get_permission(method=request.method, accessed_model=user)

            if not permission:
                return {"user": None, "exists": True}

            business_where_user_belongs = self.get_queryset().businesses_where_user_belongs(user_id=accessed_user_id)

            if not business_where_user_belongs:
                return {"user": None, "exists": True}
            
            businesses_where_user_has_permission = self.users_of_businesses_where_user_belongs(user_id=user.id, businesses=business_where_user_belongs, permission_id=permission.id)

            #no businesses where the user has permission over the accessed user
            if not businesses_where_user_has_permission:
                return {"user": None, "exists": True}
            
            return {"user": accessed_user, "exists": True}

    def businesses_allowed_to_user(self, request, model=None) -> list:
        user = request.user

        if user.is_superuser:
            Business = apps.get_model('locations', 'Business')
            businesses = Business.objects.all()
            return [b.id for b in businesses]

        if not user.is_authenticated or not user:
            return []

        allowed_businesses = self.businesses_where_user_has_user_and_grouppermission_on_model(user=user, request=request, model=model)
        return allowed_businesses

    def businesses_where_user_has_user_and_grouppermission_on_model(self, user, request, model=None) -> list:
            
            model = user if not model else model

            permission = self.get_permission(method=request.method, accessed_model=model)
            if not permission: 
                return []
            
            business_user_has_perm = self.get_queryset().get_business_where_user_has_userpermission(user=user, permission=permission)
            business_with_groups_user_belongs = self.get_queryset().get_business_groups_user_is(user=user)
            
            groups_not_allowed = []

            #searchs prohibitions for the groups the user belongs to / returns the permission ids
            if business_with_groups_user_belongs:
                groups_not_allowed = self.get_queryset().groups_forbidden_to_make_action_of_permission(permission=permission, bg_user_belongs=business_with_groups_user_belongs)

            allowed_businesses = []
            # remove businesses where the group has prohibition for the permission
            if groups_not_allowed:
                for b, g in business_with_groups_user_belongs:
                    if g not in groups_not_allowed:
                        allowed_businesses.append(b)

            # combine both lists without repeat / are the ids of the allowed businesses
            allowed_businesses = set(allowed_businesses + business_user_has_perm)

            return list(allowed_businesses)

    def users_allowed_to_user(self, request, model=None) -> list:
        user = request.user
        business_list = self.businesses_allowed_to_user(request=request, model=model)

        if not business_list:
            return []
        
        return self.users_that_belongs_to_a_business(business_list=business_list)




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
    
    def create_user(self, username, email, name, last_name, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, False, False, **extra_fields)

    def create_superuser(self, username, email, name, last_name, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, True, True, **extra_fields)
    



class User(AbstractUser):
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



