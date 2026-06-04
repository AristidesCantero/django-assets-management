from rest_framework import serializers
from users.presentation.serializers.data_manage.set_businesses import *
from users.presentation.serializers.data_manage.permission_manager import *
from users.presentation.serializers.validators.validators import *
from users.presentation.serializers.token_generator import send_verification_email 
from users.presentation.serializers.validators.validators import validate_name, validate_password, validate_last_name
from rest_framework.validators import UniqueValidator
from users.domain.models import AuthProvider, EmailVerificationToken



class UserRegisterSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = '__all__'
            extra_kwargs = {
              "password": {
                "write_only":True,
                "min_length":8,
              }
            }

        username = serializers.CharField(validators=[validate_name], required=True)
        name = serializers.CharField(validators=[validate_name], required=True)
        last_name = serializers.CharField(validators=[validate_last_name], required=True)
        email = serializers.EmailField(required=True)
        password = serializers.CharField(write_only=True, validators=[validate_password], required=True)
        
        def create(self, validated_data):
          email = validated_data["email"].lower().strip()
          password = validated_data["password"]
          
          
          #add email spam prevention checking the last time a user tried to create the user account
          
          existing = User.objects.filter(email=email).first()

          if existing and existing.email_verified:
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
            
          if existing and not existing.email_verified:
              user = existing
              raw_token = EmailVerificationToken.refresh_old_token(user)
              email_sent = send_verification_email(user, raw_token)
              print('email_sent repeated: ', email_sent)
          else:
            user = User.objects.create_user_unregistered(**validated_data)
            
            AuthProvider.objects.create(
                  user=user,
                  provider_type="password",
                  provider_uid=email
              )
          
            raw_token = EmailVerificationToken.generate_token(user)
            
            email_sent = send_verification_email(
              user,raw_token
          )
            
          return user
      
      