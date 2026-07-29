from users.domain.models import User
from locations.domain.models import Business
from users.domain.service.email_dispatcher_invitation import TokenInvitationGenerator
from users.domain.service._base_token_email_service import BaseTokenEmailService


class BusinessInvitationService(BaseTokenEmailService):
    """
    Owns the flow of sending a business-invitation token email.
    Uses TokenInvitationGenerator internally for the email-rendering concern.
    """

    def send_invitation(self, user: User, token: str, business: Business, inviter: User) -> int:
        uid = self._encode_pk(user)
        business_uid = self._encode_pk(business)
        generator = TokenInvitationGenerator('invitation_template.html')
        return generator.send_email(user, token, uid, business_uid, business, inviter)