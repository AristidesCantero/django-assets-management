from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from permissions.models import ForbiddenGroupPermissions

@receiver(m2m_changed, sender=Group.permissions.through)
def block_forbidden_permissions(sender, instance, action, pk_set, **kwargs):
    print("Se modifico un permiso de un grupo")
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