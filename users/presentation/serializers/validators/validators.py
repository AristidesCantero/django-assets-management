from django.core.exceptions import ValidationError
from permissions.domain.permissions import *
from django.contrib.auth.models import Group
from locations.domain.models import Business



def validate_all_users_permissions(instance):
        permissions_businesses_keys = set(instance.keys())
        businesses_keys = set([str(business.id) for business in Business.objects.raw("SELECT id FROM locations_business")])
        invalid_keys = permissions_businesses_keys - businesses_keys

        if invalid_keys:
            raise ValidationError(f"Invalid business IDs: {', '.join(invalid_keys)}")
        
        all_invalid_p_keys = {}

        for key in permissions_businesses_keys:
            business_p = instance[key]
            permission_keys = set(business_p.keys())
            all_p_keys = set([str(perm.id) for perm in Permission.objects.raw("SELECT id FROM auth_permission")])
            invalid_p_keys = permission_keys - all_p_keys

            if invalid_p_keys:
                all_invalid_p_keys[key] = invalid_p_keys
        
        if all_invalid_p_keys:
            error_messages = []
            for business_id, invalid_perms in all_invalid_p_keys.items():
                error_messages.append(f"( Business id {business_id} : {', '.join(invalid_perms)} )")
            raise ValidationError('Invalid permission IDs found: ' + " ; ".join(error_messages))
        
        return instance

def validate_all_users_groups(instance):

        non_existing_b = {}


        for business_key, group_instance in instance.items():
            business = Business.objects.raw("SELECT id FROM locations_business WHERE id = %s", [business_key])
            if not business:
                non_existing_b[business_key] = True


        if non_existing_b:
            raise ValidationError(f"Non existing business IDs: {', '.join(non_existing_b.keys())}")
        

        all_invalid_g_keys = {}
        for business_key, group_instance in instance.items():
            for group_key, is_marked in group_instance.items():
                gbp = Group.objects.raw("SELECT id FROM auth_group WHERE id = %s", [group_key])
                if not gbp:
                    if business_key not in all_invalid_g_keys:
                        all_invalid_g_keys[business_key] = []
                    all_invalid_g_keys[business_key].append(group_key)


        if all_invalid_g_keys:
            error_messages = []
            for business_id, invalid_groups in all_invalid_g_keys.items():
                error_messages.append(f"( Business id {business_id} : {', '.join(invalid_groups)} )")
            raise ValidationError('Invalid group IDs found: ' + " ; ".join(error_messages))
                 
def validate_all_group_permissions(instance):
        permission_keys = set(instance.keys())
        all_p_keys = set([str(perm.id) for perm in Permission.objects.raw("SELECT id FROM auth_permission")])
        invalid_p_keys = permission_keys - all_p_keys

        if invalid_p_keys:
            raise ValidationError(f"Invalid permission IDs: {', '.join(invalid_p_keys)}")
        
        return instance


            
            