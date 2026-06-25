from rest_framework.generics import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from locations.models import Business
from locations.serializers.business_serializer import BusinessListSerializer, BusinessSerializer
from permissions.domain.permission_classes.permissions import permissionToCheckModel
from rest_framework_simplejwt.authentication import JWTAuthentication
from permissions.domain.authentication import CookieJWTAuthentication


class BusinessListAPIView(ListCreateAPIView):
    serializer_class = BusinessListSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissionToCheckModel]
    http_method_names = ["get", "post"]

    def get_queryset(self, request):
        user = request.user
        businesses : list[str] = Business.objects.get_businesses_for_user(user.id)
        return Business.objects.filter(id__in=businesses)

    def get(self, request):
        businesses = self.get_queryset(request=request)
        businesses = self.serializer_class(businesses, many=True)
        
        context = {
            'data':businesses.data
        }
        return Response(context, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = self.serializer_class(data = request.data)

        response_data = {}
        if serializer.is_valid():
            serializer.save()
            response_data['data'] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data = {
            'errors': serializer.errors,
            'message': 'Error al crear el negocio'
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class BusinessAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissionToCheckModel]
    http_method_names = ['get','patch','delete']

    def get_queryset(self, business_id=None):
        return Business.objects.get(id=business_id)
    
    def get(self, request, business_id=None):
        response_data = {}
        try:
          business = self.get_queryset(business_id=business_id)
        except Business.DoesNotExist:
            response_data['message'] = "No se encontró el negocio"
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(business)
        response_data['data'] = serializer.data
        return Response(response_data, status=status.HTTP_200_OK)
          
    def patch(self, request, business_id):
        response_data = {}
        try:
          business = self.get_queryset(business_id=business_id)
        except Business.DoesNotExist:
            response_data['message'] = "No se encontró el negocio"
            return Response(response_data, status=status.HTTP_200_OK)
          
        
        serializer = self.serializer_class(business, data = request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = { 'data': serializer.data, 'message': 'Negocio actualizado correctamente' }
            return Response(response_data, status=status.HTTP_200_OK)
          
        response_data = { 'errors': serializer.errors, 'message' : 'Error al actualizar el negocio, información inválida' }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, business_id):
        response_data = {}
        try:
          business = self.get_queryset(business_id=business_id)
        except Business.DoesNotExist:
            response_data['message'] = "No se encontró el negocio"
            return Response(response_data, status=status.HTTP_200_OK)
      
        
        serializer = self.serializer_class(business)
        data = serializer.data
        response_data['data'] = data
        response_data['message'] = 'Negocio eliminado correctamente'
        business.delete()
        return Response(response_data, status=status.HTTP_200_OK)
        
            