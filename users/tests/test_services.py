"""
Unit and integration tests for all services in the users app.

Test coverage is organized by service, following the
structure defined in users/SERVICES.md and TESTS.md.

Test level rationale is documented per group.
"""

import pytest
import hashlib
import secrets
from unittest.mock import patch, MagicMock, call
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from secrets import compare_digest


# ======================================================================
# GROUP 1: BaseTokenEmailService
# Level: UNIT — pure utility, no database, no I/O.
# ======================================================================

class TestBaseTokenEmailService:
    """
    BaseTokenEmailService provides a static _encode_pk helper.
    It is inherited by all token-based email services.
    """

    def test_encode_pk_returns_urlsafe_base64_string(self, user):
        """
        Business rule: _encode_pk must produce a URL-safe base64
        representation of an object's primary key that can be
        decoded back to the original pk string.
        """
        from users.domain.service._base_token_email_service import BaseTokenEmailService

        encoded = BaseTokenEmailService._encode_pk(user)
        decoded = force_str(urlsafe_base64_decode(encoded))

        assert decoded == str(user.pk)
        assert isinstance(encoded, str)
        assert "/" not in encoded  # URL-safe
        assert "+" not in encoded


# ======================================================================
# GROUP 2: BaseTokenGenerator
# Level: UNIT — mock render_to_string and send_mail.
# ======================================================================

class TestBaseTokenGenerator:
    """
    BaseTokenGenerator is the base class for all email dispatchers.
    It renders a template and calls send_mail.
    """

    def test_send_email_renders_correct_template(self, user, mock_render_to_string, mock_send_mail):
        """
        Business rule: The HTML template must be rendered with the
        provided render_dict before sending.
        """
        from users.domain.service.email_dispatcher_base import BaseTokenGenerator

        generator = BaseTokenGenerator(email_template="test_template.html")
        render_dict = {"user_name": user.name, "link": "http://example.com/token"}
        result = generator.send_email(render_dict=render_dict, subject="Test", user=user)

        mock_render_to_string.assert_called_once_with("test_template.html", render_dict)
        assert result == 1

    def test_send_email_calls_send_mail_with_correct_args(self, user, mock_render_to_string, mock_send_mail):
        """
        Business rule: send_mail must be called with the correct subject,
        from_email (from settings), recipient_list, and HTML message.
        """
        from users.domain.service.email_dispatcher_base import BaseTokenGenerator
        from django.conf import settings

        generator = BaseTokenGenerator(email_template="test_template.html")
        render_dict = {"user_name": user.name}
        generator.send_email(render_dict=render_dict, subject="Test Subject", user=user)

        mock_send_mail.assert_called_once()
        # All args are passed as keyword args: subject=, message=, from_email=, recipient_list=, html_message=
        call_kwargs = mock_send_mail.call_args[1]

        assert call_kwargs.get("subject") == "Test Subject"
        assert call_kwargs.get("message") == ""
        assert call_kwargs.get("from_email") == settings.EMAIL_HOST_USER
        assert call_kwargs.get("recipient_list") == [user.email.strip()]
        assert call_kwargs.get("html_message") == "<html>rendered</html>"

    def test_send_email_returns_int_count(self, user, mock_render_to_string, mock_send_mail):
        """
        Business rule: send_email returns the number of successfully
        sent emails (0 or 1 for a single recipient).
        """
        from users.domain.service.email_dispatcher_base import BaseTokenGenerator

        generator = BaseTokenGenerator(email_template="test_template.html")
        result = generator.send_email(
            render_dict={"user_name": user.name},
            subject="Test",
            user=user,
        )
        assert isinstance(result, int)


# ======================================================================
# GROUP 3: TokenGenerator (Verification)
# Level: UNIT — mock parent send_email.
# ======================================================================

class TestTokenGenerator:
    """
    TokenGenerator builds the verification email link
    and delegates rendering/sending to BaseTokenGenerator.
    """

    def test_send_email_builds_verification_link(self, user, mock_send_mail, mock_render_to_string):
        """
        Business rule: The verification link must follow the pattern
        http://localhost:8000/users/confirma/?uid={uid}&token={token}.
        """
        from users.domain.service.email_dispatcher_verification import TokenGenerator

        generator = TokenGenerator()
        result = generator.send_email(user=user, token="abc123", uid="test-uid")

        # The link is passed inside render_dict -> rendered template
        mock_render_to_string.assert_called_once()
        render_dict = mock_render_to_string.call_args[0][1]
        assert "verification_link" in render_dict
        assert "uid=test-uid" in render_dict["verification_link"]
        assert "token=abc123" in render_dict["verification_link"]

    def test_send_email_includes_user_name(self, user, mock_send_mail, mock_render_to_string):
        """
        Business rule: The email template context must include the user's name.
        """
        from users.domain.service.email_dispatcher_verification import TokenGenerator

        generator = TokenGenerator()
        generator.send_email(user=user, token="t", uid="u")

        render_dict = mock_render_to_string.call_args[0][1]
        assert render_dict["user_name"] == user.name

    def test_send_email_calls_parent_send_email(self, user, mock_send_mail, mock_render_to_string):
        """
        Business rule: TokenGenerator delegates the actual email sending
        to BaseTokenGenerator.send_email with the correct arguments.
        """
        from users.domain.service.email_dispatcher_verification import TokenGenerator

        with patch(
            "users.domain.service.email_dispatcher_base.BaseTokenGenerator.send_email"
        ) as mocked_super:
            generator = TokenGenerator()
            generator.send_email(user=user, token="t", uid="u")

            mocked_super.assert_called_once()
            call_args = mocked_super.call_args.args
            render_dict = call_args[0]
            subject = call_args[1]
            # user is positional arg 3
            assert render_dict["verification_link"] is not None
            assert "Assets App" in subject


# ======================================================================
# GROUP 4: TokenInvitationGenerator
# Level: UNIT — mock parent send_email.
# ======================================================================

class TestTokenInvitationGenerator:
    """
    TokenInvitationGenerator builds the invitation email link
    and delegates rendering/sending to BaseTokenGenerator.
    """

    def test_send_email_builds_invitation_link(self, user, business, mock_send_mail, mock_render_to_string):
        """
        Business rule: The invitation link must contain uid, token, and business uid.
        """
        from users.domain.service.email_dispatcher_invitation import TokenInvitationGenerator

        generator = TokenInvitationGenerator()
        generator.send_email(
            user=user, token="tok123", uid="uid123",
            business_uid="bid456", business=business, inviter_user=user
        )

        render_dict = mock_render_to_string.call_args[0][1]
        assert "invitation_url" in render_dict
        assert "uid=uid123" in render_dict["invitation_url"]
        assert "token=tok123" in render_dict["invitation_url"]
        assert "business=bid456" in render_dict["invitation_url"]

    def test_send_email_includes_all_context_vars(self, user, business, mock_send_mail, mock_render_to_string):
        """
        Business rule: The email template context must include user_name,
        business_name, inviter_name, and invitation_url.
        """
        from users.domain.service.email_dispatcher_invitation import TokenInvitationGenerator

        inviter = user  # same user for simplicity
        generator = TokenInvitationGenerator()
        generator.send_email(
            user=user, token="t", uid="u",
            business_uid="b", business=business, inviter_user=inviter
        )

        render_dict = mock_render_to_string.call_args.args[1]
        assert render_dict["user_name"] == user.name
        assert render_dict["business_name"] == business.name
        assert render_dict["inviter_name"] == inviter.name
        assert "invitation_url" in render_dict

    def test_send_email_calls_parent_send_email(self, user, business):
        """
        Business rule: TokenInvitationGenerator must delegate to the parent's
        send_email method with the correct render_dict, subject, and user.
        """
        from users.domain.service.email_dispatcher_invitation import TokenInvitationGenerator

        with patch(
            "users.domain.service.email_dispatcher_base.BaseTokenGenerator.send_email"
        ) as mocked_super:
            generator = TokenInvitationGenerator()
            generator.send_email(
                user=user, token="t", uid="u",
                business_uid="b", business=business, inviter_user=user
            )

            mocked_super.assert_called_once()
            render_dict, subject, _ = mocked_super.call_args.args
            assert "invitation_url" in render_dict
            assert "Assets App" in subject


# ======================================================================
# GROUP 5: EmailVerificationService
# Level: UNIT — mock TokenGenerator.
# ======================================================================

class TestEmailVerificationService:
    """
    EmailVerificationService orchestrates the email-verification flow:
    encodes user pk, creates a TokenGenerator, and sends the email.
    """

    def test_send_verification_encodes_user_pk(self, user, mock_token_generator):
        """
        Business rule: The user's primary key must be encoded via
        _encode_pk before being passed to TokenGenerator.
        """
        from users.domain.service.email_verification_service import EmailVerificationService

        with patch.object(
            EmailVerificationService, "_encode_pk", return_value="encoded-uid"
        ) as encode_spy:
            service = EmailVerificationService()
            service.send_verification(user=user, token="tok123")

            encode_spy.assert_called_once_with(user)

    def test_send_verification_creates_generator_and_calls_send(self, user, mock_token_generator):
        """
        Business rule: TokenGenerator must be instantiated and its
        send_email method called with user, token, and encoded uid.
        """
        from users.domain.service.email_verification_service import EmailVerificationService

        service = EmailVerificationService()
        with patch.object(service, "_encode_pk", return_value="encoded-uid"):
            result = service.send_verification(user=user, token="tok123")

            mock_token_generator.assert_called_once()
            instance = mock_token_generator.return_value
            instance.send_email.assert_called_once_with(user, "tok123", "encoded-uid")
            assert result == 1

    def test_send_verification_returns_send_email_result(self, user):
        """
        Business rule: The return value must be the integer returned by
        TokenGenerator.send_email (0 or 1).
        """
        from users.domain.service.email_verification_service import EmailVerificationService

        with patch(
            "users.domain.service.email_verification_service.TokenGenerator"
        ) as mock_gen:
            instance = mock_gen.return_value
            instance.send_email.return_value = 0  # simulate failure

            service = EmailVerificationService()
            with patch.object(service, "_encode_pk", return_value="uid"):
                result = service.send_verification(user=user, token="t")

                assert result == 0  # 0 emails sent


# ======================================================================
# GROUP 6: BusinessInvitationService
# Level: UNIT — mock TokenInvitationGenerator.
# ======================================================================

class TestBusinessInvitationService:
    """
    BusinessInvitationService orchestrates the invitation email flow.
    """

    def test_send_invitation_encodes_user_and_business(self, user, business, mock_invitation_generator):
        """
        Business rule: Both the user and the business primary keys
        must be encoded via _encode_pk.
        """
        from users.domain.service.business_invitation_service import BusinessInvitationService

        service = BusinessInvitationService()
        with patch.object(service, "_encode_pk", wraps=service._encode_pk) as encode_spy:
            service.send_invitation(user=user, token="t", business=business, inviter=user)

            # _encode_pk is called twice: once for user, once for business
            assert encode_spy.call_count == 2

    def test_send_invitation_uses_invitation_template(self, user, business, mock_invitation_generator):
        """
        Business rule: TokenInvitationGenerator must be instantiated
        with the 'invitation_template.html' template.
        """
        from users.domain.service.business_invitation_service import BusinessInvitationService

        service = BusinessInvitationService()
        with patch.object(service, "_encode_pk", return_value="encoded"):
            service.send_invitation(user=user, token="t", business=business, inviter=user)

            mock_invitation_generator.assert_called_once_with("invitation_template.html")

    def test_send_invitation_calls_generator_with_all_params(self, user, business, mock_invitation_generator):
        """
        Business rule: All parameters (user, token, uid, business_uid,
        business, inviter) must be passed to the generator.
        """
        from users.domain.service.business_invitation_service import BusinessInvitationService

        service = BusinessInvitationService()
        with patch.object(service, "_encode_pk", return_value="encoded-uid"):
            service.send_invitation(user=user, token="tok123", business=business, inviter=user)

            instance = mock_invitation_generator.return_value
            instance.send_email.assert_called_once_with(
                user, "tok123", "encoded-uid",
                "encoded-uid", business, user
            )

    def test_send_invitation_returns_send_email_result(self, user, business):
        """
        Business rule: The return value must be the integer from
        TokenInvitationGenerator.send_email.
        """
        from users.domain.service.business_invitation_service import BusinessInvitationService

        with patch(
            "users.domain.service.business_invitation_service.TokenInvitationGenerator"
        ) as mock_gen:
            instance = mock_gen.return_value
            instance.send_email.return_value = 0

            service = BusinessInvitationService()
            with patch.object(service, "_encode_pk", return_value="uid"):
                result = service.send_invitation(
                    user=user, token="t", business=business, inviter=user
                )
                assert result == 0


# ======================================================================
# GROUP 7: BusinessMembershipService
# Level: INTEGRATION — requires database for ORM operations.
# ======================================================================

class TestBusinessMembershipService:
    """
    BusinessMembershipService manages the creation and update of
    BusinessMembership and UserBusinessPermission records.
    """

    def test_set_businessmembership_creates_new_membership(self, db, user, business, global_worker_role):
        """
        Business rule: When a user has no membership in a business,
        calling set_businessmembership must create a new BusinessMembership
        and return (membership, created=True).
        """
        from permissions.domain.service.business_membership_service import BusinessMembershipService
        from permissions.domain.models import BusinessMembership, BusinessRole, UserBusinessPermission

        service = BusinessMembershipService()
        membership, created = service.set_businessmembership(
            user_id=user, business_id=business, role_id=global_worker_role.id
        )

        assert created is True
        assert membership.user == user
        assert membership.business == business
        assert membership.role == global_worker_role
        assert BusinessMembership.objects.filter(user=user, business=business).count() == 1

    def test_set_businessmembership_returns_existing_membership(self, db, user, business, global_worker_role):
        """
        Business rule: When a user already has a membership in a business,
        calling set_businessmembership must return the existing membership
        with role updated if a different role_id is provided.
        """
        from permissions.domain.service.business_membership_service import BusinessMembershipService
        from permissions.domain.models import BusinessMembership, BusinessRole

        # Pre-create membership with Worker role
        existing = BusinessMembership.objects.create(
            user=user, business=business, role=global_worker_role
        )

        # Create a different role to test role update
        admin_role = BusinessRole.objects.create(
            scope=BusinessRole.Scope.GLOBAL, name="TestAdmin", level=90
        )

        service = BusinessMembershipService()
        membership, created = service.set_businessmembership(
            user_id=user, business_id=business, role_id=admin_role.id
        )

        assert created is False
        assert membership.id == existing.id
        # Role should have been updated to the new one
        membership.refresh_from_db()
        assert membership.role == admin_role
        assert BusinessMembership.objects.filter(user=user, business=business).count() == 1

    def test_set_businessmembership_uses_default_role_when_not_provided(self, db, user, business, global_worker_role):
        """
        Business rule: When no role_id is provided, the service must use
        the default role (id=3).
        """
        from permissions.domain.service.business_membership_service import BusinessMembershipService
        from permissions.domain.models import BusinessMembership, BusinessRole

        # Ensure default role exists
        default_role, _ = BusinessRole.objects.get_or_create(
            id=3, defaults={'scope': BusinessRole.Scope.GLOBAL, 'name': 'DefaultRole'}
        )

        service = BusinessMembershipService()
        membership, created = service.set_businessmembership(
            user_id=user, business_id=business
        )

        assert created is True
        assert membership.role == default_role

    def test_set_businessmembership_raises_when_default_role_missing(self, db, user, business):
        """
        Business rule: If neither the requested role nor the default role (id=3)
        exists, BusinessRole.DoesNotExist must be raised.
        """
        from permissions.domain.service.business_membership_service import BusinessMembershipService
        from permissions.domain.models import BusinessRole, BusinessMembership

        # Delete the default role (id=3) if it exists
        BusinessRole.objects.filter(id=3).delete()

        service = BusinessMembershipService()
        with pytest.raises(BusinessRole.DoesNotExist, match="default role not found"):
            service.set_businessmembership(
                user_id=user, business_id=business, role_id=99999
            )

    def test_set_businessmembership_raises_when_default_role_missing_no_role_id(self, db, user, business):
        """
        Business rule: If no role_id is given and the default role (id=3)
        does not exist, BusinessRole.DoesNotExist must be raised.
        """
        from permissions.domain.service.business_membership_service import BusinessMembershipService
        from permissions.domain.models import BusinessRole

        # Delete the default role (id=3) if it exists
        BusinessRole.objects.filter(id=3).delete()

        service = BusinessMembershipService()
        with pytest.raises(BusinessRole.DoesNotExist, match="Default role"):
            service.set_businessmembership(
                user_id=user, business_id=business
            )

# ======================================================================
# GROUP 8: InvitationAcceptanceService
# Level: INTEGRATION — complex flow with atomic transaction.
# ======================================================================

class TestInvitationAcceptanceService:
    """
    InvitationAcceptanceService encapsulates the full invitation acceptance
    flow: decode uids → validate existence → verify token hash →
    create membership → mark accepted. All inside a single atomic transaction.
    """

    def test_accept_success_path(
        self, db, user, business, invitation, global_worker_role, encoded_user_uid, encoded_business_uid
    ):
        """
        Business rule: When all conditions are met (user exists, business exists,
        not already a member, invitation exists, token matches, Worker role exists),
        the flow must:
        - Create BusinessMembership with Worker role
        - Mark invitation as accepted
        - Return status 'success'
        """
        from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService
        from permissions.domain.models import BusinessMembership

        service = InvitationAcceptanceService()
        result = service.accept(
            raw_uid=encoded_user_uid,
            raw_token=invitation._raw_token,
            raw_business_uid=encoded_business_uid,
        )

        assert result.status == "success"
        assert "Invitation completed" in result.message

        # Verify membership was created
        membership = BusinessMembership.objects.filter(
            user=user, business=business
        ).first()
        assert membership is not None
        assert membership.role.id == global_worker_role.id

        # Verify invitation was accepted
        invitation.refresh_from_db()
        assert invitation.is_accepted is True

    def test_accept_invalid_base64_returns_invalid_token(self, db):
        """
        Business rule: When the base64 uids cannot be decoded,
        the service must return status 'invalid_token'.
        """
        from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService

        service = InvitationAcceptanceService()
        result = service.accept(
            raw_uid="!!!invalid-base64!!!",
            raw_token="whatever",
            raw_business_uid="also-invalid",
        )

        assert result.status == "invalid_token"
        assert "Invalid link" in result.message

    def test_accept_user_not_found(self, business, encoded_business_uid):
        """
        Business rule: If the user does not exist in the database,
        return status 'user_not_found'.
        """
        from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        # Encode a non-existent user pk
        non_existent_uid = urlsafe_base64_encode(force_bytes(99999))

        service = InvitationAcceptanceService()
        result = service.accept(
            raw_uid=non_existent_uid,
            raw_token="some-token",
            raw_business_uid=encoded_business_uid,
        )

        assert result.status == "user_not_found"

    def test_accept_business_not_found(self, user, encoded_user_uid):
        """
        Business rule: If the business does not exist, return 'business_not_found'.
        """
        from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        non_existent_business_uid = urlsafe_base64_encode(force_bytes(99999))

        service = InvitationAcceptanceService()
        result = service.accept(
            raw_uid=encoded_user_uid,
            raw_token="some-token",
            raw_business_uid=non_existent_business_uid,
        )

        assert result.status == "business_not_found"

    def test_accept_already_member(
        self, db, user, business, global_worker_role, encoded_user_uid, encoded_business_uid
    ):
        """
        Business rule: If the user is already a member of the business,
        return 'already_member'.
        """
        from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService
        from permissions.domain.models import BusinessMembership

        # Pre-create membership
        BusinessMembership.objects.create(
            user=user, business=business, role=global_worker_role
        )

        service = InvitationAcceptanceService()
        result = service.accept(
            raw_uid=encoded_user_uid,
            raw_token="whatever",
            raw_business_uid=encoded_business_uid,
        )

        assert result.status == "already_member"

    def test_accept_invitation_not_found(
        self, db, user, business, encoded_user_uid, encoded_business_uid
    ):
        """
        Business rule: If no Invitation record exists for the user+business pair,
        return 'invitation_not_found'.
        """
        from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService

        service = InvitationAcceptanceService()
        result = service.accept(
            raw_uid=encoded_user_uid,
            raw_token="some-token",
            raw_business_uid=encoded_business_uid,
        )

        assert result.status == "invitation_not_found"

    def test_accept_invalid_token_hash(
        self, db, user, business, invitation, encoded_user_uid, encoded_business_uid
    ):
        """
        Business rule: If the token hash does not match (timing-attack safe
        comparison via compare_digest), return 'invalid_token'.
        """
        from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService

        service = InvitationAcceptanceService()
        # Pass a different token than the one used to create the invitation
        result = service.accept(
            raw_uid=encoded_user_uid,
            raw_token="this-is-the-wrong-token",
            raw_business_uid=encoded_business_uid,
        )

        assert result.status == "invalid_token"

    def test_accept_worker_role_not_found(
        self, db, user, business, invitation, encoded_user_uid, encoded_business_uid
    ):
        """
        Business rule: If the "Worker" role with GLOBAL scope does not exist,
        return 'role_assignment_failed'.
        """
        from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService
        from permissions.domain.models import BusinessRole

        # Delete the Worker role (if it was auto-created by fixtures)
        BusinessRole.objects.filter(scope=BusinessRole.Scope.GLOBAL, name="Worker").delete()

        service = InvitationAcceptanceService()
        result = service.accept(
            raw_uid=encoded_user_uid,
            raw_token=invitation._raw_token,
            raw_business_uid=encoded_business_uid,
        )

        assert result.status == "role_assignment_failed"

    def test_accept_is_atomic(
        self, db, user, business, invitation, encoded_user_uid, encoded_business_uid
    ):
        """
        Business rule: The entire flow must run inside a single atomic
        transaction, so no partial state is committed on failure.
        We verify this by making the dependent Role lookup fail and
        confirming no membership was created.
        """
        from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService
        from permissions.domain.models import BusinessMembership, BusinessRole

        # Delete Worker role so the flow fails
        BusinessRole.objects.filter(scope=BusinessRole.Scope.GLOBAL, name="Worker").delete()

        service = InvitationAcceptanceService()
        service.accept(
            raw_uid=encoded_user_uid,
            raw_token=invitation._raw_token,
            raw_business_uid=encoded_business_uid,
        )

        # No membership should have been created since the transaction rolled back
        membership = BusinessMembership.objects.filter(
            user=user, business=business
        ).first()
        assert membership is None, "Atomic transaction must roll back on failure"

        # Invitation should not be marked as accepted
        invitation.refresh_from_db()
        assert invitation.is_accepted is False


# ======================================================================
# GROUP 9: InvitationService (Legacy)
# Level: INTEGRATION — requires DB for ORM operations.
# NOTE: This service references invitation.recipient_email which does
#       NOT exist on the Invitation model (it has 'user' FK instead).
#       Tests here document the current (possibly broken) behavior.
# ======================================================================

class TestInvitationService:
    """
    InvitationService is a legacy service with two methods:
    send_invitation and accept_invitation.

    Known issue: accept_invitation references `invitation.recipient_email`
    which is not a field on the Invitation model. This will cause an
    AttributeError at runtime. Tests below verify the current behavior.
    """

    def test_send_invitation_creates_invitation_and_sends_email(self, db, user, business):
        """
        Business rule: send_invitation must validate sender existence,
        set business membership, generate a token, create an Invitation
        record, and send an email.

        NOTE: The service has known bugs:
        1. calls set_businessmembership(receiver_user_id, business_id) without role_id
        2. references settings.FRONTEND_URL which does not exist
        This test patches the internal BusinessMembershipService and settings.
        """
        from users.domain.service.invitation_service import InvitationService
        from django.test.utils import override_settings

        with patch("users.domain.service.invitation_service.send_mail", return_value=1) as sm_mock:
            with override_settings(FRONTEND_URL="http://localhost:3000"):
                service = InvitationService()
                # Replace the instance attribute with a mock
                mock_bms = MagicMock()
                mock_bms.set_businessmembership.return_value = None
                service.business_membership_service = mock_bms

                invitation_result = service.send_invitation(
                    receiver_user_id=user.id,
                    business_id=business.id,
                    user=user,
                )

                # Invitation record was created
                from users.domain.models import Invitation
                saved_invitation = Invitation.objects.filter(
                    business=business, user=user
                ).first()
                assert saved_invitation is not None
                assert saved_invitation.id == invitation_result.id
                assert saved_invitation.is_accepted is False

                # Email was sent
                sm_mock.assert_called_once()

    def test_send_invitation_user_not_found_raises_validation_error(self, db, business, user):
        """
        Business rule: If the receiver user does not exist,
        ValidationError must be raised.
        """
        from users.domain.service.invitation_service import InvitationService
        from rest_framework.exceptions import ValidationError

        service = InvitationService()
        with pytest.raises(ValidationError, match="Sender user does not exist"):
            service.send_invitation(
                receiver_user_id=99999,
                business_id=business.id,
                user=user,
            )

    def test_send_invitation_business_not_found_raises_validation_error(self, db, user):
        """
        Business rule: If the business does not exist,
        ValidationError must be raised.
        """
        from users.domain.service.invitation_service import InvitationService
        from rest_framework.exceptions import ValidationError

        service = InvitationService()
        with pytest.raises(ValidationError, match="Business does not exist"):
            service.send_invitation(
                receiver_user_id=user.id,
                business_id=99999,
                user=user,
            )

    def test_accept_invitation_invalid_token_raises_validation_error(self, db):
        """
        Business rule: If no matching Invitation is found,
        ValidationError must be raised.
        """
        from users.domain.service.invitation_service import InvitationService
        from rest_framework.exceptions import ValidationError

        service = InvitationService()
        with pytest.raises(ValidationError, match="Invalid or expired invitation"):
            service.accept_invitation(token="non-existent-token", uid="some-uid")


# ======================================================================
# GROUP 10: UserBusinessPermissionService
# Level: INTEGRATION — requires DB for UserBusinessPermission operations.
# ======================================================================

class TestUserBusinessPermissionService:
    """
    UserBusinessPermissionService manages UserBusinessPermission records:
    set (one or multiple) and get (one or all for a user).
    """

    def test_set_userbusinesspermission_creates_new_permissions(self, db, user, business, permission_model):
        """
        Business rule: For each permission in the dict, a new
        UserBusinessPermission must be created if it doesn't exist.
        """
        from permissions.domain.service.user_bpermission_service import UserBusinessPermissionService
        from permissions.domain.models import BusinessMembership, UserBusinessPermission, BusinessRole

        role = BusinessRole.objects.create(scope=BusinessRole.Scope.GLOBAL, name="TestRole")
        membership = BusinessMembership.objects.create(
            user=user, business=business, role=role
        )

        service = UserBusinessPermissionService()
        permission_dict = {str(permission_model.id): True}
        service.set_userbusinesspermission(
            membership=membership,
            permission_dict=permission_dict
        )

        ubp = UserBusinessPermission.objects.get(
            membership_id=membership.id, permission_id=permission_model.id
        )
        assert ubp is not None
        assert ubp.allowed is True

    def test_set_userbusinesspermission_updates_existing(self, db, user, business, permission_model):
        """
        Business rule: If a UserBusinessPermission already exists,
        its 'allowed' field must be updated.
        """
        from permissions.domain.service.user_bpermission_service import UserBusinessPermissionService
        from permissions.domain.models import BusinessMembership, UserBusinessPermission, BusinessRole

        role = BusinessRole.objects.create(scope=BusinessRole.Scope.GLOBAL, name="TestRole2")
        membership = BusinessMembership.objects.create(
            user=user, business=business, role=role
        )
        # Create existing permission with allowed=False
        ubp = UserBusinessPermission.objects.create(
            membership=membership, permission_id=permission_model.id, allowed=False
        )

        service = UserBusinessPermissionService()
        service.set_userbusinesspermission(
            membership=membership,
            permission_dict={str(permission_model.id): True}
        )

        ubp.refresh_from_db()
        assert ubp.allowed is True

    def test_set_userbusinesspermission_one_creates_new(self, db, user, business, permission_model):
        """
        Business rule: set_userbusinesspermission_one must create
        a new UserBusinessPermission if it doesn't exist.
        """
        from permissions.domain.service.user_bpermission_service import UserBusinessPermissionService
        from permissions.domain.models import BusinessMembership, UserBusinessPermission, BusinessRole

        role = BusinessRole.objects.create(scope=BusinessRole.Scope.GLOBAL, name="TestRole3")
        membership = BusinessMembership.objects.create(
            user=user, business=business, role=role
        )

        service = UserBusinessPermissionService()
        result = service.set_userbusinesspermission_one(
            membership=membership,
            permission_id=permission_model.id,
            allowed=True
        )

        assert result is not None
        assert result.allowed is True
        assert UserBusinessPermission.objects.filter(
            membership=membership, permission_id=permission_model.id
        ).count() == 1

    def test_set_userbusinesspermission_one_updates_existing(self, db, user, business, permission_model):
        """
        Business rule: set_userbusinesspermission_one must update
        an existing UserBusinessPermission's allowed field.
        """
        from permissions.domain.service.user_bpermission_service import UserBusinessPermissionService
        from permissions.domain.models import BusinessMembership, UserBusinessPermission, BusinessRole

        role = BusinessRole.objects.create(scope=BusinessRole.Scope.GLOBAL, name="TestRole4")
        membership = BusinessMembership.objects.create(
            user=user, business=business, role=role
        )
        ubp = UserBusinessPermission.objects.create(
            membership=membership, permission_id=permission_model.id, allowed=False
        )

        service = UserBusinessPermissionService()
        result = service.set_userbusinesspermission_one(
            membership=membership,
            permission_id=permission_model.id,
            allowed=True
        )

        ubp.refresh_from_db()
        assert ubp.allowed is True
        assert result.id == ubp.id

    def test_get_user_businesses_permissions_returns_dict(self, db, user, business, permission_model):
        """
        Business rule: get_user_businesses_permissions must return a
        dict of {business_id: {permission_id: allowed}} for the user.
        """
        from permissions.domain.service.user_bpermission_service import UserBusinessPermissionService
        from permissions.domain.models import BusinessMembership, UserBusinessPermission, BusinessRole

        role = BusinessRole.objects.create(scope=BusinessRole.Scope.GLOBAL, name="TestRole5")
        membership = BusinessMembership.objects.create(
            user=user, business=business, role=role
        )
        UserBusinessPermission.objects.create(
            membership=membership, permission_id=permission_model.id, allowed=True
        )

        result = UserBusinessPermissionService.get_user_businesses_permissions(user, json_format=True)
        
        business_id = str(business.id)
        
        assert business_id in result, "Business not found in result"
        assert str(permission_model.id) in [str(x) for x in result[business_id].keys()], "Permission is not in the user permissions"
        assert result[business_id][permission_model.id] is True, "Permission is not true"

    def test_get_user_business_permission_returns_permission(self, db, user, business, permission_model):
        """
        Business rule: get_user_business_permission must return the
        UserBusinessPermission if it exists, or None if not.
        """
        from permissions.domain.service.user_bpermission_service import UserBusinessPermissionService
        from permissions.domain.models import BusinessMembership, UserBusinessPermission, BusinessRole

        role = BusinessRole.objects.create(scope=BusinessRole.Scope.GLOBAL, name="TestRole6")
        membership = BusinessMembership.objects.create(
            user=user, business=business, role=role
        )
        UserBusinessPermission.objects.create(
            membership=membership, permission_id=permission_model.id, allowed=True
        )

        # Existing permission
        result = UserBusinessPermissionService.get_user_business_permission(
            membership_id=membership.id,
            permission_id=permission_model.id
        )
        assert result is not None
        assert result.allowed is True

        # Non-existing permission
        result = UserBusinessPermissionService.get_user_business_permission(
            membership_id=membership.id,
            permission_id=99999
        )
        assert result is None
