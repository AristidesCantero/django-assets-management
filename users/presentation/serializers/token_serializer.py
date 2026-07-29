from rest_framework_simplejwt.serializers import TokenBlacklistSerializer as BaseTokenBlacklistSerializer, TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class TokenBlacklistSerializer(BaseTokenBlacklistSerializer):
    """
    Custom TokenBlacklistSerializer that handles token blacklisting via create method.
    """
    
    def create(self, validated_data):
        """
        Blacklist the refresh token.
        
        Args:
            validated_data: Dictionary containing the validated refresh token
            
        Returns:
            Dictionary with the blacklisted token information
        """
        refresh_token = validated_data.get('refresh_token')
        
        # Parse the token
        token = RefreshToken(refresh_token)
        
        # Blacklist the token
        token.blacklist()
        
        return {
            'refresh': str(token),
            'blacklisted': True
        }
    
    def validate(self, attrs):
        """
        Validate the refresh token and prepare for blacklisting.
        """
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Overrides TokenObtainPairSerializer to include extra verification for user when login"""
    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.email_verified:
            raise serializers.ValidationError(
                "User account pending of confirmation."
            )

        return data