from permissions.domain.models import UserBusinessPermission, BusinessMembership
from django.db import transaction
from users.domain.service.base import BaseService


class UserBusinessPermissionService(BaseService):
    """
    Manages UserBusinessPermission records:
    set (one or multiple) and get (one or all for a user).
    """

    @transaction.atomic
    def set_userbusinesspermission(self, membership: BusinessMembership, permission_dict: dict):
        """
        Set UserBusinessPermission records for a membership from a dict.

        Args:
            membership_id: BusinessMembership instance or id
            permission_dict: dict of {permission_id (str): allowed (bool)}
        """
        for permission_id, allowed in permission_dict.items():
            user_business_permission, created = UserBusinessPermission.objects.select_for_update().get_or_create(
                membership=membership,
                permission_id=permission_id,
                defaults={'allowed': allowed}
            )

            if not created:
                user_business_permission.allowed = allowed
                user_business_permission.save(update_fields=['allowed'])

    @transaction.atomic
    def set_userbusinesspermission_one(self, membership, permission_id, allowed):
        """
        Set a single UserBusinessPermission for a membership.

        Args:
            membership_id: BusinessMembership instance or id
            permission_id: Permission instance or id
            allowed: bool

        Returns:
            UserBusinessPermission instance
        """
        user_business_permission, created = UserBusinessPermission.objects.select_for_update().get_or_create(
            membership=membership,
            permission_id=permission_id,
            defaults={'allowed': allowed}
        )

        if not created:
            user_business_permission.allowed = allowed
            user_business_permission.save(update_fields=['allowed'])

        return user_business_permission

    @staticmethod
    def get_user_businesses_permissions(user, json_format=True):
        """
        Get all UserBusinessPermissions for a user across all businesses.

        Uses proper ORM queries via BusinessMembership -> UserBusinessPermission.

        Args:
            user: User instance
            json_format: if True, permission keys are ids; if False, they are names

        Returns:
            dict of {business_id: {permission_id/name: allowed}}
        """
        memberships = BusinessMembership.objects.filter(user=user).prefetch_related(
            'userbusinesspermission_set__permission'
        )

        businesses_permissions = {}
        for membership in memberships:
            business_id = str(membership.business_id)
            businesses_permissions[business_id] = {}

            for ubp in membership.userbusinesspermission_set.all():
                perm_key = (
                    ubp.permission_id
                    if json_format
                    else ubp.permission.name
                )
                businesses_permissions[business_id][perm_key] = ubp.allowed

        return businesses_permissions

    @staticmethod
    def get_user_business_permission(membership_id, permission_id):
        """
        Get a single UserBusinessPermission.

        Args:
            membership_id: BusinessMembership instance or id
            permission_id: Permission instance or id

        Returns:
            UserBusinessPermission instance or None
        """
        try:
            return UserBusinessPermission.objects.get(
                membership=membership_id,
                permission_id=permission_id
            )
        except UserBusinessPermission.DoesNotExist:
            return None