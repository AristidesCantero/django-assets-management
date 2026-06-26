from rest_framework import generics, serializers
from ..serializers import BusinessMembershipSerializer, BusinessMembershipsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from ...models import BusinessMembership, BusinessRole, UserBusinessPermission
from ...domain.authentication import CookieJWTAuthentication
from ...domain.permission_classes.permissions import permissionsToCheckUser, permissionsToCheckUsers
from rest_framework.response import Response

class BusinessMembershipListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BusinessMembershipsSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, permissionsToCheckUsers]
    allowed_http_methods = ["GET"]

    def get_queryset(self):
        business_id = self.kwargs.get('business_id')
        return BusinessMembership.objects.filter(business_id=business_id)
      
    def get(self, request, business_id):
      queryset = self.get_queryset()
      serializer = self.serializer_class(queryset, many=True, context={'business_id':business_id})
      response_data = {}
      response_data['data'] = serializer.data
      return Response(response_data, status= status.HTTP_200_OK)
      
      

class BusinessMembershipDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessMembershipSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, permissionsToCheckUser]
    allowed_http_methods = ["GET", "POST"]

    def get_queryset(self):
        business_id = self.kwargs.get('business_id')
        user_id = self.kwargs.get('user_id')
        
        return BusinessMembership.objects.get(business_id=business_id, user_id=user_id)
      
    def get(self, request, business_id, user_id):
      try:
        queryset = self.get_queryset()
      except BusinessMembership.DoesNotExist:
        return Response({'message':'User membership invalid'}, status=status.HTTP_404_NOT_FOUND)
        
      serializer = self.serializer_class(queryset, context={'business_id':business_id})
      response_data = {}
      response_data['data'] = serializer.data
      return Response(response_data, status= status.HTTP_200_OK)
      