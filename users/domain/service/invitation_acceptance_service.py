from dataclasses import dataclass
from typing import Literal
from django.db import transaction
from django.utils.http import urlsafe_base64_decode
import hashlib
from secrets import compare_digest
from users.domain.models import User, Invitation
from users.domain.service.base import BaseService
from permissions.domain.models import Business, BusinessRole, BusinessMembership


@dataclass
class InvitationAcceptanceResult:
    status: Literal[
        "success", "user_not_found", "business_not_found",
        "invitation_not_found", "already_member",
        "invalid_token", "role_assignment_failed"
    ]
    message: str


class InvitationAcceptanceService(BaseService):
    """
    Encapsulates the full invitation acceptance flow:
    decode uids → validate existence → verify token hash → create membership → mark accepted.
    All database operations run inside a single atomic transaction.
    """

    DEFAULT_ROLE_NAME = "Worker"

    @transaction.atomic
    def accept(self, raw_uid: str, raw_token: str, raw_business_uid: str) -> InvitationAcceptanceResult:
        # 1. Decode base64-encoded uids
        try:
            user_id = urlsafe_base64_decode(raw_uid).decode()
            business_id = urlsafe_base64_decode(raw_business_uid).decode()
        except Exception:
            return InvitationAcceptanceResult("invalid_token", "Invalid link")

        # 2. Resolve objects (graceful existence checks)
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return InvitationAcceptanceResult("user_not_found", "User not found")

        business = Business.objects.filter(pk=business_id).first()
        if not business:
            return InvitationAcceptanceResult("business_not_found", "Business not found")

        # 3. Already a member?
        if BusinessMembership.objects.filter(user=user, business=business).exists():
            return InvitationAcceptanceResult("already_member", "User already in business")

        # 4. Retrieve invitation
        invitation = Invitation.objects.filter(user=user, business=business).first()
        if not invitation:
            return InvitationAcceptanceResult("invitation_not_found", "Invalid invitation")

        # 5. Verify token — matches Invitation.generate_token() hashing
        received_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        if not compare_digest(invitation.token, received_hash):
            return InvitationAcceptanceResult("invalid_token", "Invalid or expired token")

        # 6. Get the default Worker role
        worker_role = BusinessRole.objects.filter(
            scope=BusinessRole.Scope.GLOBAL,
            name=self.DEFAULT_ROLE_NAME
        ).first()
        if not worker_role:
            return InvitationAcceptanceResult(
                "role_assignment_failed",
                "Fallo la asignación de rol del usuario en la empresa"
            )

        # 7. Create membership + mark invitation as accepted
        try:
            BusinessMembership.objects.create(
                user=user, business=business, role=worker_role
            )
            invitation.is_accepted = True
            invitation.save()
        except Exception:
            return InvitationAcceptanceResult(
                "role_assignment_failed",
                "Fallo la integración del usuario en el negocio"
            )

        return InvitationAcceptanceResult(
            "success",
            f"Invitation completed for business {business}"
        )