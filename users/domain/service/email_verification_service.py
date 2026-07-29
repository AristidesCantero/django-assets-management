from users.domain.models import User
from users.domain.service.email_dispatcher_verification import TokenGenerator
from users.domain.service._base_token_email_service import BaseTokenEmailService


class EmailVerificationService(BaseTokenEmailService):
    """
    Owns the flow of sending a user email-verification token.
    Uses TokenGenerator internally for the email-rendering concern.
    """

    def send_verification(self, user: User, token: str) -> int:
        uid = self._encode_pk(user)
        generator = TokenGenerator()
        return generator.send_email(user, token, uid)