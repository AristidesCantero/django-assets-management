from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from users.presentation.serializers.tokenserializer import TokenBlacklistSerializer
from permissions.domain.authentication import CookieJWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from appcore.settings.base import SIMPLE_JWT, DEBUG

class CustomizedTokenObtainPairView(TokenObtainPairView):
    """
    Override the default TokenObtainPairView to set access/refresh tokens as HttpOnly cookies.
    """
    def post(self, request, *args, **kwargs):
        # Get tokens using the default TokenObtainPairView logic
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
 
        # Extract tokens from the serializer
        access_token = serializer.validated_data["access"]
        refresh_token = serializer.validated_data["refresh"]
 
        # Create a response (no tokens in the body)
        response = Response({"detail": "Tokens generated successfully"})
 
        # Set access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # Prevent JavaScript access
            secure=not DEBUG,  # Use HTTPS in production
            samesite="Strict",  # Mitigate CSRF
            max_age= SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],  # 15 minutes (matches ACCESS_TOKEN_LIFETIME)
            path="/",  # Cookie sent to all routes
        )
 
        # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not DEBUG,
            samesite="Strict",
            max_age=SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],  # 1 day (matches REFRESH_TOKEN_LIFETIME)
            path="/",
        )
 
        return response


class CustomizedTokenRefreshView(TokenRefreshView):
    """
    Override TokenRefreshView to read the refresh token from a cookie and set a new access token cookie.
    """
    def post(self, request, *args, **kwargs):
        # Extract refresh token from the "refresh_token" cookie
        refresh_token = request.COOKIES.get("refresh_token")
        
        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies"},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        # Use the refresh token to get a new access token
        serializer = self.get_serializer(data={'refresh':refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
 
        # Extract the new access token
        new_access_token = serializer.validated_data["access"]
 
        # Create a response and set the new access token cookie
        response = Response({"detail": "Token refreshed successfully"})
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,#not DEBUG,
            samesite="Strict",
            max_age=SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],  # 15 minutes
            path="/",
        )
        
 
        return response
    
    
    
class CustomizedTokenBlackListLogout(TokenBlacklistView):
    serializer_class = TokenBlacklistSerializer
    authentication_classes = [CookieJWTAuthentication]
    def post(self, request, *args, **kwargs):
        # Extract refresh token from the "refresh_token" cookie
        refresh_token = request.COOKIES.get("refresh_token")
        
        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use the refresh token to get a new access token
        refresh_serializer = self.get_serializer(data={"refresh": refresh_token})
        
        try:
            refresh_serializer.is_valid(raise_exception=True)
        except Exception as e:
            Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Blacklist the refresh token
        refresh_serializer.save()

        # Create a response and clear the cookies
        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response