from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.http.request import HttpHeaders
from django.middleware.csrf import CsrfViewMiddleware
from typing import Optional
import json


class CSRFValidator:
    """
    Enforces Django's CSRF check for API requests that carry an authenticated
    session (the access_token cookie).

    Because the global CsrfViewMiddleware only enforces on /admin/ paths
    (see appcore/middleware.py), this validator is the sole CSRF enforcer for
    API views. CsrfViewMiddleware.process_view returns a 403 response (built
    by CSRF_FAILURE_VIEW) when the token is missing/invalid; anything other
    than None here means the request was rejected.
    """

    def __init__(self):
        self.middleware = CsrfViewMiddleware(lambda request: None)

    def validate(self, request):
        #print("CSRF header:", request.META.get("HTTP_X_CSRFTOKEN"))
        #print("CSRF cookie:", request.COOKIES.get("csrftoken"))
        #print("All headers:", dict(request.headers))
        #print("All cookies:", request.COOKIES)
        response = self.middleware.process_view(
            request,
            lambda request: None,
            (),
            {},
        )
        if response is not None:
            # process_view rejected the request (CSRF failure view response).
            reason = self._extract_reason(response)
            raise PermissionDenied(reason or "CSRF verification failed.")

    @staticmethod
    def _extract_reason(response):
        """
        Extract the rejection reason embedded in the CSRF failure view
        response. The custom JSON failure view (appcore.errors.csrf_failure_json)
        includes it under "details"; fall back gracefully for other views.
        """
        try:
            payload = json.loads(response.content)
            return payload.get("details")
        except (ValueError, AttributeError):
            return getattr(response, "reason_phrase", "CSRF verification failed.")


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class to extract the access token from an HttpOnly cookie.
    """

    def __init__(self):
        super().__init__()
        self.csrf_validator = CSRFValidator()

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not user.email_verified:
            raise AuthenticationFailed(
                "User pending for confirmation."
            )
        return user

    def authenticate(self, request):
        # CSRF is only meaningful for requests carrying an authenticated
        # session cookie. Anonymous requests (no access_token cookie) skip
        # the check so public endpoints (registration, login, csrf-token)
        # remain open and stateless.
        if "access_token" in request.COOKIES:
            self.csrf_validator.validate(request)
        authentication = super().authenticate(request)
        return authentication

    def cookies_to_dict(self, cookies: str) -> dict:
        if not cookies:
            return {}

        fields = cookies.split(";")
        return {field.split("=")[0].strip(): field.split("=")[1] for field in fields}

    def get_header(self, request):
        return request.headers

    def get_raw_token(self, header: HttpHeaders) -> Optional[bytes]:
        # Read the access token from the "access_token" cookie

        cookies = header.get("Cookie")
        if not cookies:
            return None

        cookies = self.cookies_to_dict(cookies=cookies)
        if "access_token" not in cookies:
            return None

        access_token = cookies["access_token"]
        return access_token.encode("utf-8")