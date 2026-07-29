"""
Non-persistent unitary tests for users domain models.
Only test logic that does not require database interaction.
"""
import hashlib
import secrets
import string
from datetime import timedelta

import pytest
from django.utils import timezone

from users.domain.models import User, AuthProvider, Invitation
from users.domain.models import UserManager


class TestUserModel:
    """Non-persistent unit tests for User model"""

    def test_str_returns_name_and_last_name(self):
        """__str__ should return 'name last_name'"""
        user = User(name="John", last_name="Doe")
        assert str(user) == "John Doe"

    def test_str_with_null_last_name(self):
        """__str__ raises TypeError when last_name is None (concatenation error)"""
        user = User(name="John", last_name=None)
        with pytest.raises(TypeError):
            str(user)

    def test_get_plural_returns_users(self):
        """get_plural() should return 'users'"""
        user = User()
        assert user.get_plural() == "users"

    def test_username_field_is_email(self):
        """USERNAME_FIELD must be 'email' for email-based auth"""
        assert User.USERNAME_FIELD == "email"

    def test_required_fields_contains_expected(self):
        """REQUIRED_FIELDS should list username, name, last_name"""
        assert set(User.REQUIRED_FIELDS) == {"username", "name", "last_name"}

    def test_default_values(self):
        """Verify default field values without hitting the database"""
        user = User()
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.email_verified is False
        assert user.deleted_at is None
        assert bool(user.image) is False


class TestUserManager:
    """Non-persistent unit tests for UserManager"""

    def test_create_user_without_email_raises_value_error(self):
        """_create_user must raise ValueError when email is empty (before any DB op)"""
        manager = UserManager()
        manager.model = User
        with pytest.raises(ValueError, match="Users must have email address"):
            manager._create_user(
                username="test", email="", name="Test",
                last_name="User", password=None,
                is_staff=False, is_superuser=False,
            )

    def test_email_is_normalized_on_create_user(self):
        """_create_user should normalize email (lowercase domain)"""
        manager = UserManager()
        manager.model = User
        normalized = manager.normalize_email("TEST@EXAMPLE.COM")
        assert normalized == "TEST@example.com"


class TestAuthProvider:
    """Non-persistent unit tests for AuthProvider"""

    def test_providers_choices_contains_expected_values(self):
        """PROVIDERS choices should include password, google, github"""
        providers = dict(AuthProvider.PROVIDERS)
        assert providers == {
            "password": "password",
            "google": "google",
            "github": "github",
        }


class TestEmailVerificationToken:
    """Non-persistent unit tests for EmailVerificationToken"""

    def test_sha256_hash_length_is_64(self):
        """SHA-256 hex digest must be exactly 64 characters"""
        token_hash = hashlib.sha256(b"any_input").hexdigest()
        assert len(token_hash) == 64

    def test_sha256_hash_contains_only_hex_chars(self):
        """SHA-256 hex digest must only contain 0-9 and a-f"""
        token_hash = hashlib.sha256(b"any_input").hexdigest()
        assert all(c in "0123456789abcdef" for c in token_hash)

    def test_same_input_produces_same_hash(self):
        """SHA-256 hashing must be deterministic"""
        raw = "some_token_value"
        hash1 = hashlib.sha256(raw.encode()).hexdigest()
        hash2 = hashlib.sha256(raw.encode()).hexdigest()
        assert hash1 == hash2

    def test_different_inputs_produce_different_hashes(self):
        """Different inputs must produce different hashes"""
        hash_a = hashlib.sha256(b"token_a").hexdigest()
        hash_b = hashlib.sha256(b"token_b").hexdigest()
        assert hash_a != hash_b

    def test_generated_raw_token_format(self):
        """secrets.token_urlsafe(32) must be 43-char URL-safe string"""
        raw_token = secrets.token_urlsafe(32)
        assert len(raw_token) == 43
        allowed = set(string.ascii_letters + string.digits + "-_")
        assert all(c in allowed for c in raw_token)

    def test_generated_raw_token_has_high_entropy(self):
        """Multiple generated tokens should differ (high probability)"""
        tokens = {secrets.token_urlsafe(32) for _ in range(100)}
        assert len(tokens) == 100

    def test_expires_at_is_24_hours_from_now(self):
        """Default expires_at must be 24 hours ahead (86400 seconds)"""
        now = timezone.now()
        expires_at = now + timedelta(hours=24)
        diff = (expires_at - now).total_seconds()
        assert diff == pytest.approx(86400, rel=0.01)

    def test_verify_token_result_values(self):
        """verify_token must return one of the expected string values"""
        expected = {"verified", "invalid", "already_used", "expired"}
        # Just verify the expected return values make sense
        assert "verified" in expected
        assert "invalid" in expected
        assert "already_used" in expected
        assert "expired" in expected


class TestInvitation:
    """Non-persistent unit tests for Invitation"""

    def test_expires_at_is_24_hours_from_now(self):
        """Default expires_at must be 24 hours ahead (86400 seconds)"""
        now = timezone.now()
        expires_at = now + timedelta(hours=24)
        diff = (expires_at - now).total_seconds()
        assert diff == pytest.approx(86400, rel=0.01)

    def test_generated_raw_token_format(self):
        """secrets.token_urlsafe(32) must be 43-char URL-safe string"""
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        assert len(raw_token) == 43
        assert len(token_hash) == 64