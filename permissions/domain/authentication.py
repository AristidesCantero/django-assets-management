
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http.request import HttpHeaders
from typing import Optional, TypeVar
import re

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class to extract the access token from an HttpOnly cookie.
    """
    
    def cookies_to_dict(self, cookies: str)-> dict:
        if not cookies:
            return None
        
        fields = cookies.split(";")
        return {field.split("=")[0]:field.split("=")[1] for field in fields}

    def get_header(self, request):
        return request.headers
   
    
    def get_raw_token(self, header: HttpHeaders) -> Optional[bytes]:
        # Read the access token from the "access_token" cookie
        cookies = header.get('Cookie')
        if not cookies:
            return None
        
        cookies = self.cookies_to_dict(cookies=cookies)
        access_token = cookies['access_token']
        return access_token.encode('utf-8') or None
    