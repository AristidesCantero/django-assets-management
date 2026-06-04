from permissions.domain.models import BusinessMembership, UserBusinessPermission, BusinessRole
from django.db import transaction


class BusinessMembershipManager:
    @transaction.atomic
    def set_businessmembership(self, user_id, business_id, role_id):
        # Check if the user already has a BusinessMembership
        business_membership, created = BusinessMembership.objects.select_for_update().get_or_create(
            user=user_id,
            business=business_id,
            defaults={
              "role":3
            }
        )
        businessrole = BusinessRole.objects.filter(id=role_id).first()
        if businessrole:  
          business_membership.role = businessrole
          business_membership.save()
          
          

    @transaction.atomic
    def set_userbusinesspermission(self, membership_id, permission_dict):
        # Check if the user already has a UserBusinessPermission for each permission
        for permission_id, allowed in permission_dict.items():
            user_business_permission, created = UserBusinessPermission.objects.select_for_update().get_or_create(
                membership=membership_id,
                permission_id=permission_id,
                defaults={}
            )
            
            user_business_permission.allowed = allowed
            user_business_permission.save()
