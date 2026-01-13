from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from users.models import User

from permissions.models import ForbiddenGroupPermissions

@receiver(m2m_changed, sender=Group.permissions.through)
def block_forbidden_permissions(sender, instance, action, pk_set, **kwargs):
    """
    Evita que un grupo obtenga permisos que están prohibidos en ForbiddenGroupPermission.
    """
    if action in ["pre_add", "pre_set"]: 
        forbidden_ids = ForbiddenGroupPermissions.objects.filter(
            group=instance
        ).values_list("permission_id", flat=True)

        forbidden_attempts = set(pk_set).intersection(forbidden_ids)

        if forbidden_attempts:
            raise ValidationError(
                f"El grupo '{instance.name}' tiene prohibido uno o más permisos que intentas asignar."
            )
        


@receiver(post_save, sender=User)
def user_default_profile(sender, instance, created, **kwargs):
    print("Se creo o modifico un usuario")
    """
    Asigna permisos y grupos predeterminados a un usuario al crearlo.
    """