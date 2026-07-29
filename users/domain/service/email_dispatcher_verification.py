from users.domain.service.email_dispatcher_base import BaseTokenGenerator


class TokenGenerator(BaseTokenGenerator):
    def __init__(self, email_template=None):
        email_template = email_template or "email_template.html"
        super().__init__(email_template)

    def send_email(self, user, token, uid) -> int:
        """
        Send an email with the token url using the HTML email template.
        Returns: the number of successfull emails, since is 1 email there are only 0 or 1
        """
        verification_link = f"http://localhost:8000/users/confirma/?uid={uid}&token={token}"
        subject = "Assets App verificación de usuario"
        render_dict = {
            'user_name': user.name,
            'verification_link': verification_link,
        }

        #send the email with parent class 
        return super().send_email(render_dict,subject,user)