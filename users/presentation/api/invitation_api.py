from rest_framework.response import Response
from rest_framework.generics import *
from users.presentation.serializers.invitation_serializer import UserInvitationSerializer
from users.domain.models import User, Invitation
from permissions.domain.models import BusinessRole
from permissions.domain.authentication import CookieJWTAuthentication
from permissions.domain.permission_classes.permissions import *
from rest_framework import status
from django.utils.http import urlsafe_base64_decode
from secrets import compare_digest
import hashlib


class InvitationAPIView(GenericAPIView):
    serializer_class = UserInvitationSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissionToInviteUsers]
    allowed_methods = ['post']
    
    def get_queryset(self):
        return []
  
    def post(self, request):
        sender_user = request.user
        serializer = self.serializer_class(
            data=request.data, context={"sender":sender_user}
        )
        
        
        if serializer.is_valid(raise_exception=True):      
          serializer.save()
          return Response(
              {"message": "Invitation email sent"},
              status=status.HTTP_201_CREATED
          )
          
        
        return Response({'error':'Failed send verification email'}, status=status.HTTP_400_BAD_REQUEST)



class InvitationAcceptAPIView(RetrieveAPIView):
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
            membership = BusinessMembership.objects.filter(user=user_id, business=business_id)
            if membership:
              return Response({"message":"User already in business"})
            
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
            invitation.is_accepted = True
            business_role = BusinessRole.objects.get(scope=BusinessRole.Scope.GLOBAL, name="Worker")
            membership = BusinessMembership.objects.create(user=user,business=business,role=business_role)
            #logic in case the invitation is accepted
            invitation.save()
            return Response({"message": f"Invitation completed for business {membership.business}"})
          except BusinessRole.DoesNotExist:
              return Response({"error": 'Fallo la asignación de rol del usuario en la empresa'},status=500)
          except:
              return Response({"error":"Fallo la integración del usuario en el negocio"},status=500)
          

        return Response(
            {"error": "Invalid or expired token"},
            status=400
        )