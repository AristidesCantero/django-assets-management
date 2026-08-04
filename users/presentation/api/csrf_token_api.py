from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class CSRFTokenView(APIView):
    """
    Public endpoint that initializes (or reuses) the CSRF token for the
    consuming service.

    GET /users/csrf-token/

    Response:
        200 {"csrfToken": "..."}

    Side effects:
        - The `csrftoken` cookie is set on the response (written by
          AdminOnlyCsrfMiddleware.process_response, which reads the
          CSRF_COOKIE_NEEDS_UPDATE flag set by get_token()).
        - The external service must send the returned token in the
          X-CSRFToken header (or the raw cookie value) on subsequent
          state-changing requests that carry the access_token cookie.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        token = get_token(request)
        return Response(
            {"csrfToken": token},
            status=status.HTTP_200_OK,
        )