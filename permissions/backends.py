from django.contrib.auth.backends import BaseBackend
from .models import Company, CompanyPermission, UserGroup
from django.contrib.auth.models import Permission
from locations.models import Business
from django.db.models import ForeignKey, OneToOneField
from django.core.exceptions import ObjectDoesNotExist
from permissions.models import UserBusinessPermission, GroupBusinessPermission
from django.contrib.auth.models import Group



class BusinessPermissionBackend(BaseBackend):
    """
    has_perm(user, perm, obj=None)
    - perm puede venir como 'app_label.codename' o 'codename'
    - obj puede ser Company o un objeto con atributo .company
    """

    #retorna el Business asociado al modelo obj
    def _get_business_from_obj(self, obj, visited=None):
        
        if visited is None:
            visited = set()
        if obj is None or obj in visited:
            return None
        visited.add(obj)
        if isinstance(obj, Business):
            return obj
        
        fields = obj._meta.get_fields()
        business = None

        for field in fields:
            if isinstance(field, (ForeignKey, OneToOneField)):
                try:
                    related_obj = getattr(obj, field.name)
                except ObjectDoesNotExist:
                    continue

                if related_obj is None:
                    continue

                business = self._get_business_from_obj(related_obj)
                if business:
                    return business
        return None



    def _get_group_business_permission(self, user, business, codename):
        try:
            user_groups = Group.objects.filter(user=user)

            for group in user_groups:
                group_permission = GroupBusinessPermission.objects.filter(
                    business_key=business,
                    group_key=group,
                    permission__codename=codename
                ).first()
                if group_permission:
                    return group_permission
            return None

        except Group.DoesNotExist:
            return None

    def _get_user_business_permission(self, user, business, codename):
        try:
            
            user_permission = UserBusinessPermission.objects.filter(
                user_key=user,
                business_key=business,
                permission=permission
            ).first()

            permission = Permission.objects.get(codename=codename)
            return user_permission
        except Permission.DoesNotExist:
            return None
        except UserBusinessPermission.DoesNotExist:
            return None


    #verifica si el usuario tiene permiso de empresa sobr el objeto
    def has_perm(self, user_obj, perm, obj=None):
        # 1) superuser short-circuit
        if getattr(user_obj, "is_superuser", False):
            return True

        # 2) si no está autenticado o inactivo
        if not getattr(user_obj, "is_active", False):
            return False

        business = self._get_business_from_obj(obj)
        # opcional: permitir permisos globales si company es None y existe CompanyPermission con company=None
        # extra: soportar perm como 'app_label.codename' o 'codename'
        codename = perm.split(".")[-1]

        # 3) permisos directos de usuario para esa empresa
        if business:
            # 4) permisos por grupo: obtener grupos del usuario
            group_b_perm = self._get_group_business_permission(user_obj.groups.all(), codename)
            # 5) permisos directos de usuario para esa empresa
            user_b_perm = self._get_user_business_permission(user_obj, business, codename)


            if group_b_perm:
                return True
            if user_b_perm:
                return True

        

        return False