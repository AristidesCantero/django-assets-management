from rest_framework.response import Response
from rest_framework.generics import *
from rest_framework import status
from users.presentation.serializers.user_serializer import UserSerializer
from users.presentation.serializers.register_serializers import UserRegisterSerializer
from permissions.domain.permissions import *
from permissions.domain.authentication import CookieJWTAuthentication
from users.domain.models import User, EmailVerificationToken
from django.db import connection
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from django.conf import settings
from secrets import compare_digest
import hashlib




def sqlQuery(query: str, params: tuple = ()):
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return results


def path_has_primary_key(path: str) -> bool:
    segments = path.strip('/').split('/')
    primary_key = segments[-1]
    return primary_key if primary_key.isdigit() else None



class UserAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissionsToCheckUsers]
    http_method_names = ["get", "patch", "delete"]
    
    
    def get_queryset(self,user_id):
        pass

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, user_id):
        try:
            user = self.get_queryset(user_id=user_id)
            response_data = {
                'data': self.serializer_class(user,context={'request': request}).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
 
    def patch(self, request, pk, *args, **kwargs):
        try:
            user = self.get_queryset(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            
            serializer.update(user, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        try:
            user = self.get_queryset(pk=pk)
            user_serializer_data = self.serializer_class(user, context={'request': request}).data
            user.delete()
            return Response({'detail': 'User has been deleted successfully.', "data": user_serializer_data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
    


class UserListAPIView(RetrieveAPIView):
    serializer_class = UserSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissionsToCheckUsers]
    http_method_names = ["get"]
    
    def get_queryset(self, pk):
        user_data = User.objects.user_is_allowed_to_check_user(request=self.request, consulted_user_id=pk)
        if not user_data["exists"] or not user_data['user']:
            raise User.DoesNotExist
        return user_data["user"]

    def get(self, request, pk, *args, **kwargs):
        try:
            user = self.get_queryset(pk=pk)
            response_data = {
                'data': self.serializer_class(user,context={'request': request}).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
    
    


class UserRegisterAPIView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    http_method_names = ["post"]
    
    
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data
        )
        
 
        if serializer.is_valid(raise_exception=True):      
          serializer.save()
          return Response(
              {"message": "Verification email sent"},
              status=status.HTTP_201_CREATED
          )
        
        return Response({'error':'Failed send verification email'}, status=status.HTTP_400_BAD_REQUEST)



class UserRegisterConfirmationAPIView(RetrieveAPIView):
      
    def get(self, request):
        uid = request.GET.get("uid")
        received_token = request.GET.get("token")

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
            
            email_token = EmailVerificationToken.objects.filter(user_id=user_id).first()
            
        except User.DoesNotExist:
          return Response({"error":"user not found"},status=400)
        

        except Exception:
            return Response(
                {"error": "Invalid link"},
                status=400
            )
            
            
        #alternate check_password(recieved_token, verification.token_hash)
        received_hash = hashlib.sha256(
          received_token.encode()
          ).hexdigest()

        token_matches = compare_digest(
        email_token.token_hash,
        received_hash
    )
        print(email_token.token_hash)
        print(received_hash)

        if token_matches:
            user.is_active = True
            user.email_verified = True
            user.save()

            return Response({"message": "Email verified"})

        return Response(
            {"error": "Invalid or expired token"},
            status=400
        )



class MailTesting(RetrieveUpdateDestroyAPIView):
    def get(self, request):
      
      
        html_message = render_to_string(self.email_template, {
            'user_name': "usuario_aleatorio",
            'verification_email': "aqui no hay correo",
        })

        # Send the email
        return send_mail(
                subject='Your Verification Token',
                message='',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=["aristidescantero2000@hotmail.com"],
                html_message=html_message,
                fail_silently=False,
        )
        
        return Response({'message':'mail send, verify'}, status=status.HTTP_200_OK)


    
    