from permissions.domain.models import BusinessMembership, BusinessRole
from django.db import transaction, IntegrityError
from users.domain.service.base import BaseService


class BusinessMembershipService(BaseService):
    @transaction.atomic
    def set_businessmembership(self, user_id, business_id, role_id=None):
        """
        Set a BusinessMembership for a user in a business.
        If the membership already exists for (user, business), it is returned.
        If not, a new one is created with the given role (or default role 3).

        Returns:
            tuple: (BusinessMembership instance, bool created)

        Raises:
            BusinessRole.DoesNotExist: If the given role_id is invalid and
                                       the default role (id=3) also doesn't exist.
            IntegrityError: If the get_or_create fails due to DB constraints.
        """
        # 1. Resolve the role
        role = None
        if role_id is not None:
            try:
                role = BusinessRole.objects.get(id=role_id)
            except BusinessRole.DoesNotExist:
                try:
                    role = BusinessRole.objects.get(id=3)
                except BusinessRole.DoesNotExist:
                    raise BusinessRole.DoesNotExist("Invalid role, default role not found")
        else:
            # No role_id provided — use the default role (id=3)
            try:
                role = BusinessRole.objects.get(id=3)
            except BusinessRole.DoesNotExist:
                raise BusinessRole.DoesNotExist("Default role (id=3) not found")

        # 2. Get or create the membership — role goes in defaults so lookup is (user, business) only
        try:
            business_membership, created = BusinessMembership.objects.select_for_update().get_or_create(
                user=user_id,
                business=business_id,
                defaults={'role': role}
            )
        except IntegrityError as e:
            raise IntegrityError(
                f"Failed to create BusinessMembership for user={user_id}, "
                f"business={business_id}: {e}"
            )

        # If the membership was not created (already existed), update the role
        if not created:
            if business_membership.role != role:
                business_membership.role = role
                business_membership.save()

        return business_membership, created
      
    