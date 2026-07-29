from abc import ABC
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from users.domain.service.base import BaseService


class BaseTokenEmailService(BaseService, ABC):
    """
    Shared utility for any service that sends a token-based email.
    Provides a static uid-encoding helper used by all subclasses.
    """

    @staticmethod
    def _encode_pk(obj) -> str:
        return urlsafe_base64_encode(force_bytes(obj.pk))