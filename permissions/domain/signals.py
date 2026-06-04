from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from users.domain.models import User


@receiver(m2m_changed, sender=Group.permissions.through)
def block_forbidden_permissions(sender, instance, action, pk_set, **kwargs):
    pass
        


@receiver(post_save, sender=User)
def user_default_profile(sender, instance, created, **kwargs):
    pass