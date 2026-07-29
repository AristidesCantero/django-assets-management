"""
Shared fixtures for users app service tests.

Provides:
- Model instances (user, business, role, group, permission, etc.)
- Mock fixtures for email/send_mail
- Factory-like fixtures for common objects
"""

import pytest
from unittest.mock import patch, MagicMock
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


# ------------------------------------------------------------------
# Model fixtures (database-backed, for integration tests)
# ------------------------------------------------------------------

@pytest.fixture
def user(db):
    """Create a regular unverified user."""
    from users.domain.models import User
    user = User.objects.create_user_unregistered(
        username="testuser",
        email="testuser@example.com",
        name="Test",
        last_name="User",
        password="securepassword123",
    )
    return user


@pytest.fixture
def verified_user(db):
    """Create a verified user."""
    from users.domain.models import User
    user = User.objects.create_user_unregistered(
        username="verifieduser",
        email="verified@example.com",
        name="Verified",
        last_name="User",
        password="securepassword123",
    )
    user.email_verified = True
    user.save(update_fields=["email_verified"])
    return user


@pytest.fixture
def superuser(db):
    """Create a superuser."""
    from users.domain.models import User
    admin = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        name="Admin",
        last_name="User",
        password="adminpass123",
    )
    return admin


@pytest.fixture
def business(db):
    """Create a test business."""
    from locations.domain.models import Business
    return Business.objects.create(
        name="Test Business",
        tin="1234567890",
        utr="TEST-UTR-001",
    )


@pytest.fixture
def global_worker_role(db):
    """Create the default Worker role with GLOBAL scope, if not existing."""
    from permissions.domain.models import BusinessRole
    role, _ = BusinessRole.objects.get_or_create(
        scope=BusinessRole.Scope.GLOBAL,
        name="Worker",
        defaults={"description": "Default worker role"},
    )
    return role


@pytest.fixture
def admin_group(db):
    """Return the ADMIN group (usually created by migration)."""
    from django.contrib.auth.models import Group
    group, _ = Group.objects.get_or_create(name="ADMIN")
    return group


@pytest.fixture
def manager_group(db):
    """Return the MANAGER group."""
    from django.contrib.auth.models import Group
    group, _ = Group.objects.get_or_create(name="MANAGER")
    return group


@pytest.fixture
def permission_model(db):
    """Return a sample Permission instance."""
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    from users.domain.models import User
    ct, _ = ContentType.objects.get_or_create(
        app_label="users", model="user"
    )
    perm, _ = Permission.objects.get_or_create(
        codename="test_permission",
        content_type=ct,
        defaults={"name": "Test Permission"},
    )
    return perm


@pytest.fixture
def invitation(db, user, business):
    """Create a pending invitation with a known raw token."""
    import hashlib
    import secrets
    from users.domain.models import Invitation
    from django.utils import timezone
    from datetime import timedelta

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    inv = Invitation.objects.create(
        user=user,
        business=business,
        token=token_hash,
        expires_at=timezone.now() + timedelta(hours=24),
    )
    # Attach raw token so tests can construct the matching plaintext
    inv._raw_token = raw_token
    return inv


@pytest.fixture
def business_membership(db, verified_user, business, global_worker_role):
    """Create a business membership for verified_user."""
    from permissions.domain.models import BusinessMembership
    membership, _ = BusinessMembership.objects.get_or_create(
        user=verified_user,
        business=business,
        defaults={"role": global_worker_role},
    )
    return membership


# ------------------------------------------------------------------
# Encoded-uid helpers
# ------------------------------------------------------------------

@pytest.fixture
def encoded_user_uid(user):
    """Return base64-encoded uid for the default user."""
    return urlsafe_base64_encode(force_bytes(user.pk))


@pytest.fixture
def encoded_business_uid(business):
    """Return base64-encoded uid for the default business."""
    return urlsafe_base64_encode(force_bytes(business.pk))


# ------------------------------------------------------------------
# Mock fixtures for email services
# ------------------------------------------------------------------

@pytest.fixture
def mock_send_mail():
    """Mock send_mail where it's imported in the email dispatcher base."""
    with patch(
        "users.domain.service.email_dispatcher_base.send_mail", return_value=1
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_render_to_string():
    """Mock render_to_string where it's imported in the email dispatcher base."""
    with patch(
        "users.domain.service.email_dispatcher_base.render_to_string",
        return_value="<html>rendered</html>",
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_token_generator():
    """Mock TokenGenerator class used by EmailVerificationService."""
    with patch(
        "users.domain.service.email_verification_service.TokenGenerator"
    ) as mocked:
        instance = mocked.return_value
        instance.send_email.return_value = 1
        yield mocked


@pytest.fixture
def mock_invitation_generator():
    """Mock TokenInvitationGenerator class used by BusinessInvitationService."""
    with patch(
        "users.domain.service.business_invitation_service.TokenInvitationGenerator"
    ) as mocked:
        instance = mocked.return_value
        instance.send_email.return_value = 1
        yield mocked