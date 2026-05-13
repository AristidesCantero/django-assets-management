from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404

def custom_exception_handler(exc, context):
    # Let DRF handle it first}
    
    print("EXCEPCION: ")
    print(exc)
    print("CONTEXTO")
    print(context)
    response = exception_handler(exc, context)

    # Handle DRF-generated errors (including NotFound)
    if response is not None:
        return Response({
            "error": True,
            "message": _extract_message(response.data),
            "details": response.data
        }, status=response.status_code)

    # Handle Django-native 404 (important!)
    if isinstance(exc, Http404):
        return Response({
            "error": True,
            "message": "Resource not found",
            "details": None
        }, status=status.HTTP_404_NOT_FOUND)

    # Fallback (optional but recommended)
    return Response({
        "error": True,
        "message": "Internal server error",
        "details": None
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _extract_message(data):
    """
    Normalize DRF error formats into a readable message.
    """
    if isinstance(data, dict):
        return next(iter(data.values()))  # first error
    if isinstance(data, list):
        return data[0]
    return str(data)