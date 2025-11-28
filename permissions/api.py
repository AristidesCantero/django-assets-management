from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from permissions.serializers import *
from permissions.models import ForbiddenGroupPermissions


    

class ForbiddenGroupPermissionsDetailAPI(RetrieveUpdateDestroyAPIView):
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ForbiddenGroupPermissionsSerializer
    queryset = ForbiddenGroupPermissions.objects.all()


    def get(self, request, pk, *args, **kwargs):
        try:
            fpermission = ForbiddenGroupPermissions.objects.get(pk=pk)
            serializer = self.serializer_class(fpermission)
            return Response(serializer.data)
        except ForbiddenGroupPermissions.DoesNotExist:
            return Response({"detail": "Forbidden permission not found."}, status=status.HTTP_404_NOT_FOUND)
        
    
    def put(self, request, pk, *args, **kwargs):
        try:
            fpermission = ForbiddenGroupPermissions.objects.get(pk=pk)
        except ForbiddenGroupPermissions.DoesNotExist:
            return Response({"detail": "Forbidden permission not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(fpermission, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        try:
            fpermission = ForbiddenGroupPermissions.objects.get(pk=pk)
            serialized_data = self.serializer_class(fpermission).data
            fpermission.delete()
            response_data = {}
            response_data['data'] = serialized_data
            return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        except ForbiddenGroupPermissions.DoesNotExist:
            return Response({"detail": "Forbidden permission not found."}, status=status.HTTP_404_NOT_FOUND)

    
        



class ForbiddenGroupPermissionsListCreateAPI(ListCreateAPIView):
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ForbiddenGroupPermissionsListSerializer
    queryset = ForbiddenGroupPermissions.objects.all()


    def get(self, request, *args, **kwargs):
        try:
            fpermission = ForbiddenGroupPermissions.objects.all()
            response_data = {}
            response_data['data'] = self.serializer_class(fpermission, many=True).data
            return Response(response_data, status=status.HTTP_200_OK)
        except ForbiddenGroupPermissions.DoesNotExist:
            return Response({'detail': 'Forbidden permission has not been found.'}, status=status.HTTP_404_NOT_FOUND)

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)