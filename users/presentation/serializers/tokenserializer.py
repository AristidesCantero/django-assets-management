from rest_framework_simplejwt.serializers import TokenBlacklistSerializer as BaseTokenBlacklistSerializer
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
