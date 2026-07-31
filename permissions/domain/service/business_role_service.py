from permissions.domain.models import BusinessMembership, BusinessRole
from django.db import transaction, IntegrityError
from users.domain.service.base import BaseService


class BusinessRoleService(BaseService):
    @transaction.atomic
    def set_businessrole(self, user_id, business_id, role_id=None):
      pass