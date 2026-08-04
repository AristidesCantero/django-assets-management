"""
Custom CSRF middleware for the stateless JWT + CSRF architecture.

Because the global CsrfViewMiddleware is removed from MIDDLEWARE (CSRF is
enforced per-view inside CookieJWTAuthentication), AdminOnlyCsrfMiddleware
splits Django's CSRF machinery:

- process_request (inherited from CsrfViewMiddleware): always runs. Loads the
  csrftoken cookie secret into request.META["CSRF_COOKIE"] so the
  CookieJWTAuthentication validator can compare it against the X-CSRFToken
  header on API requests.
- process_view (overridden): enforces CSRF only for Django admin (/admin/)
  and other non-API paths. API views are covered by CookieJWTAuthentication;
  public API endpoints (login, register, csrf-token) are intentionally not
  enforced here.
- process_response (inherited): always runs. Writes the csrftoken cookie
  whenever get_token()/rotate_token() flagged CSRF_COOKIE_NEEDS_UPDATE
  (e.g. the csrf-token endpoint or after login).
"""

from django.middleware.csrf import CsrfViewMiddleware


class AdminOnlyCsrfMiddleware(CsrfViewMiddleware):
    """
    Runs Django's CSRF machinery for request preparation and cookie writing
    on every request, but only ENFORCES token validation on non-API paths
    (Django admin).

    API request paths (users/, assets/, protocol/, locations/, permissions/,
    swagger/, redoc/) are handled by the per-view CSRF check inside
    CookieJWTAuthentication.
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if not request.path.startswith("/admin/"):
            # Skip enforcement for API and public endpoints. The CSRF check
            # for API views happens inside CookieJWTAuthentication.authenticate.
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)