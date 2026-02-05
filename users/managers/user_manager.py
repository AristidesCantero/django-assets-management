from django.db import models
from users.querysets import BusinessPermissionQuerySet

class BusinessPermissionManager(models.Manager):
    def get_queryset(self):
        return BusinessPermissionQuerySet(self.model, using=self._db)

    def for_user_with_perm(self, user, perm):
        return self.get_queryset().for_user_with_perm(user, perm)