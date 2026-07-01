
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist
from permissions.presentation.serializers import PermissionSerializer

class PermissionListAPIView(generics.ListAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all permissions
        return Permission.objects.all()
      
    def get(self, request):
        permissions = self.get_queryset()
        serializer = self.serializer_class(permissions, many=True)
        
        response_data = {}
        response_data['data'] = serializer.data
        
        return Response(response_data, status = status.HTTP_200_OK)
        

class PermissionDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.all()
    
    
    def get_queryset(self, permission_id):
        return Permission.objects.get(id=permission_id)
      
    def get(self, request, permission_id):
        try:
            permission = self.get_queryset(permission_id)
            serializer = self.serializer_class(permission)
            return Response(serializer.data)
        except Permission.DoesNotExist:
            return Response({'detail': 'Permission not found'}, status=404)