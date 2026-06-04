from rest_framework.exceptions import ValidationError
from permissions.domain.models import Business, UserBusinessPermission
from users.domain.models import User, Invitation
from users.presentation.serializers.data_manage.set_businesses import BusinessMembershipManager
from django.core.mail import send_mail
from django.conf import settings
import hashlib
import secrets
import uuid
import random


class InvitationService:
    def __init__(self):
        self.business_membership_manager = BusinessMembershipManager()
        

    def send_invitation(self, receiver_user_id, business_id, user):
        try:
            # 1. Validate sender
            receiver_user = User.objects.get(id=receiver_user_id)
            business = Business.objects.get(id=business_id)

            # 2. Check if sender is already a member of the business
            self.business_membership_manager.set_businessmembership(receiver_user_id, business_id)

            # 3. Generate a unique token
            token = str(uuid.uuid4()) + str(random.randint(1000, 9999))

            # 4. Create the invitation
            invitation = Invitation.objects.create(
                business=business,
                user=user,
                token=token
            )

            # 5. Send the invitation via email
            invitation_link = f"{settings.FRONTEND_URL}/accept-invitation/{token}"
            send_mail(
                subject="You've been invited to join a business",
                message=f"Click the link to accept the invitation: {invitation_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user],
                fail_silently=False,
            )

            return invitation

        except User.DoesNotExist:
            raise ValidationError("Sender user does not exist.")
        except Business.DoesNotExist:
            raise ValidationError("Business does not exist.")



    def accept_invitation(self, token, uid):
        try:
            invitation = Invitation.objects.get(token=token, is_accepted=False)
            business = invitation.business
            recipient_email = invitation.recipient_email

            # 1. Create the user (if not already exists)
            user, created = User.objects.get_or_create(email=recipient_email)
            if not created:
                raise ValidationError("User with this email already exists.")

            # 2. Set the business membership
            self.business_membership_manager.set_businessmembership(user.id, business.id)

            # 3. Set the user business permissions
            for permission in business.permissions.all():
                UserBusinessPermission.objects.get_or_create(
                    user_id=user.id,
                    permission_id=permission.id,
                    defaults={'allowed': True}
                )

            # 4. Mark the invitation as accepted
            invitation.is_accepted = True
            invitation.save()

            return {
                'message': 'Invitation accepted successfully.',
                'user': user.id,
                'business': business.id
            }

        except Invitation.DoesNotExist:
            raise ValidationError("Invalid or expired invitation.")
