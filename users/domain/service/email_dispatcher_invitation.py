from users.domain.service.email_dispatcher_base import BaseTokenGenerator


class TokenInvitationGenerator(BaseTokenGenerator):
  
    def __init__(self, email_template=None):
        email_template = email_template or "email_template.html"
        super().__init__(email_template)

    def send_email(self, user, token, uid, business_uid, business, inviter_user) -> int:
        """
        Send an email with the token url using the HTML email template.
        Returns: the number of successfull emails, since is 1 email there are only 0 or 1
        """
        invitation_url = f"http://localhost:8000/users/accept-invitation/?uid={uid}&token={token}&business={business_uid}"
        user_name = user.name
        business_name = business.name
        inviter_name = inviter_user.name
        subject = "Assets App verificación de usuario"
        render_dict = {'invitation_url':invitation_url,'business_name':business_name, 'inviter_name':inviter_name, 'user_name':user_name
        }

        #send the email with parent class 
        return super().send_email(render_dict,subject,user)