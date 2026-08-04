"""End-to-end CSRF flow verification.

NOTE: Django's test Client disables CSRF enforcement by default. All clients
here use enforce_csrf_checks=True so the real CSRF validator
(CSRFValidator in CookieJWTAuthentication) actually runs.
"""

import pytest
from django.test import Client


@pytest.fixture
def csrf_flow_user(db):
    from users.domain.models import User

    user = User.objects.create_user_unregistered(
        username="csrfuser",
        email="csrfuser@example.com",
        name="Csrf",
        last_name="User",
        password="securepassword123",
    )
    user.email_verified = True
    user.save(update_fields=["email_verified"])
    return user


def _get_csrf_token(client):
    resp = client.get("/users/csrf-token/")
    assert resp.status_code == 200, resp.content
    return resp.json()["csrfToken"]


def _login(client, email, password, csrf_token):
    return client.post(
        "/users/token/",
        data={"email": email, "password": password},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )


def test_pre_login_csrf_token_still_valid_after_login(db, csrf_flow_user):
    """The csrftoken cookie secret is NOT rotated on login (no rotate_token)."""
    client = Client(enforce_csrf_checks=True)

    pre_login_token = _get_csrf_token(client)

    login = _login(client, csrf_flow_user.email, "securepassword123", pre_login_token)
    assert login.status_code == 200, login.content

    # Logout enforces CookieJWTAuthentication -> CSRF is checked when the
    # access_token cookie is present. The pre-login masked token must still
    # validate because the cookie secret was not rotated during login.
    resp = client.post(
        "/users/logout/",
        data={},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=pre_login_token,
    )
    assert resp.status_code == 200, (
        f"Pre-login CSRF token should stay valid after login; got {resp.status_code}: {resp.content}"
    )


def test_unknown_csrf_token_rejected(db, csrf_flow_user):
    """CSRF enforcement is real: a garbage token is rejected on logout."""
    client = Client(enforce_csrf_checks=True)

    _get_csrf_token(client)

    login = _login(client, csrf_flow_user.email, "securepassword123", "z" * 64)
    assert login.status_code == 200, login.content

    resp = client.post(
        "/users/logout/",
        data={},
        content_type="application/json",
        HTTP_X_CSRFTOKEN="z" * 64,
    )
    assert resp.status_code == 403, (
        f"Garbage CSRF token must be rejected; got {resp.status_code}: {resp.content}"
    )


def test_missing_csrf_token_rejected(db, csrf_flow_user):
    """A request without the X-CSRFToken header is rejected."""
    client = Client(enforce_csrf_checks=True)

    _get_csrf_token(client)

    login = _login(client, csrf_flow_user.email, "securepassword123", "z" * 64)
    assert login.status_code == 200, login.content

    resp = client.post(
        "/users/logout/",
        data={},
        content_type="application/json",
    )
    assert resp.status_code == 403, (
        f"Missing CSRF token must be rejected; got {resp.status_code}: {resp.content}"
    )