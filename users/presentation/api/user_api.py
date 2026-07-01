from rest_framework.response import Response
from rest_framework.generics import *
from rest_framework import status
from users.presentation.serializers.user_serializer import UserSerializer
from users.presentation.serializers.register_serializers import UserRegisterSerializer
from users.domain.models import User, EmailVerificationToken, Invitation
from permissions.domain.permission_classes.permissions import *
from permissions.domain.authentication import CookieJWTAuthentication
from permissions.domain.models import BusinessRole
from django.db import connection
from django.core.mail import send_mail
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
    permission_classes = [permissionsToCheckUser]
    http_method_names = ["get", "patch", "delete"]
    
    
    def get_queryset(self,user_id,business_id) -> User | None:
        user = User.objects.get_user_if_in_business(business_id, user_id)
        if not user or not user.is_active:
          raise User.DoesNotExist
        return user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, user_id, business_id):
        try:
            user = self.get_queryset(user_id=user_id, business_id=business_id)
            response_data = {
                'data': self.serializer_class(user,context={'request': request,'user_id':user_id, 'business_id':business_id}).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
 
    def patch(self, request, user_id, business_id):
        try:
            user = self.get_queryset(user_id=user_id, business_id=business_id)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(user, data=request.data, partial=True, context={'request': request,'user_id':user_id, 'business_id':business_id})
        if serializer.is_valid():
            serializer.update(user, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, user_id, business_id):
        try:
            user = self.get_queryset(user_id=user_id, business_id=business_id)
            serializer = self.serializer_class(user, context={'request': request,'user_id':user_id, 'business_id':business_id})
            serializer.soft_delete(user, {"is_active": False})
            return Response({'detail': 'User has been deleted successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
    


class UserListAPIView(RetrieveAPIView):
    serializer_class = UserSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissionsToCheckUsers]
    http_method_names = ["get"]
    
    def get_queryset(self, business_id) -> QuerySet[User]:
        
        user_data = User.objects.get_business_users(business_id)
        return user_data

    def get(self, request, business_id):
        try:
            if not request.business:
              return Response({'message':'invalid business ID'}, status=status.HTTP_404_NOT_FOUND)
            user = self.get_queryset(business_id=business_id)
            response_data = {
                'data': self.serializer_class(user,context={'request': request},many=True).data
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
            
        if user.email_verified:
              return Response({"message":"User already verified"}, status=status.HTTP_208_ALREADY_REPORTED)
            
            
        #alternate check_password(recieved_token, verification.token_hash)
        received_hash = hashlib.sha256(
          received_token.encode()
          ).hexdigest()

        token_matches = compare_digest(
        email_token.token_hash,
        received_hash
    )

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


    allowed_methods = ['get']

    def get(self, request):
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')
        business_uid = request.query_params.get('business')

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            business_id = urlsafe_base64_decode(business_uid).decode()
            user = User.objects.get(pk=user_id)
            business = Business.objects.get(pk=business_id)
            invitation = Invitation.objects.get(user_id=user,business=business)
        except User.DoesNotExist:
            return Response({"error":"user not found"},status=400)
        except Business.DoesNotExist:
            return Response({"error":"business not found"},status=400)
        except Invitation.DoesNotExist:
            return Response({"error":"Invalid invitation"},status=400)
        except Exception:
            return Response({"error": "Invalid link"}, status=400)
            
            
        #alternate check_password(recieved_token, verification.token_hash)
        received_hash = hashlib.sha256(
          token.encode()
          ).hexdigest()

        token_matches = compare_digest(
        invitation.token,
        received_hash
    )

        if token_matches:
          try:
            business_role = BusinessRole.objects.get(scope=BusinessRole.Scope.GLOBAL, name="Worker")
            membership = BusinessMembership.objects.create(user=user,business=business,role=business_role)
            #logic in case the invitation is accepted

            return Response({"message": "Invitation completed"})
          except BusinessRole.DoesNotExist:
              return Response({"error": 'Fallo la asignación de rol del usuario en la empresa'},status=500)
          except:
              return Response({"error":"Fallo la integración del usuario en el negocio"},status=500)
          

        return Response(
            {"error": "Invalid or expired token"},
            status=400
        )