from rest_framework.response import Response
from rest_framework.generics import *
from users.presentation.serializers.invitation_serializer import UserInvitationSerializer
from permissions.domain.authentication import CookieJWTAuthentication
from permissions.domain.permissions.permissions import *
from rest_framework import status
from users.domain.service.invitation_acceptance_service import InvitationAcceptanceService


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

        service = InvitationAcceptanceService()
        result = service.accept(
            raw_uid=uid,
            raw_token=token,
            raw_business_uid=business_uid,
        )

        status_mapping = {
            "success": ({"message": result.message}, status.HTTP_200_OK),
            "already_member": ({"message": result.message}, status.HTTP_200_OK),
            "user_not_found": ({"error": result.message}, status.HTTP_400_BAD_REQUEST),
            "business_not_found": ({"error": result.message}, status.HTTP_400_BAD_REQUEST),
            "invitation_not_found": ({"error": result.message}, status.HTTP_400_BAD_REQUEST),
            "invalid_token": ({"error": result.message}, status.HTTP_400_BAD_REQUEST),
            "role_assignment_failed": ({"error": result.message}, status.HTTP_500_INTERNAL_SERVER_ERROR),
        }

        body, http_status = status_mapping.get(
            result.status,
            ({"error": "Invalid link"}, status.HTTP_400_BAD_REQUEST)
        )
        return Response(body, status=http_status)
