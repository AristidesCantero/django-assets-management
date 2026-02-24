from rest_framework.generics import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from locations.models import Business
from locations.serializers.business_serializer import BusinessListSerializer, BusinessSerializer
from permissions.domain.permissions import permissionToCheckModel
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.querysets import BusinessQuerySet


class BusinessListAPIView(ListCreateAPIView):
    serializer_class = BusinessListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionToCheckModel]
    allowed_methods = ["GET", "POST"]

    def get_queryset(self, request):
        user = request.user
        if not user or  not user.is_authenticated:
            return []
        
        if user.is_superuser:
            return Business.objects.all()

        allowed_businesses = BusinessQuerySet.user_allowed_businesses(user=user, request=request)
        return self.serializer_class.Meta.model.objects.filter(pk__in=allowed_businesses)

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionToCheckModel]
    allowed_methods = ['get','patch','delete']

    def get_queryset(self, pk=None):
        return self.serializer_class.Meta.model.objects.filter(id=pk).first()
    
    def get(self, request, pk=None):
        business = self.get_queryset(pk=pk)
        response_data = {}
        if business:
            serializer = self.serializer_class(business)
            response_data['data'] = serializer.data
            return Response(response_data, status=status.HTTP_200_OK)
        response_data['errors'] = 'No se ha encontrado el negocio'
        response_data['message'] = 'El negocio no existe'
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
    

    def patch(self, request, pk):
        business = self.get_queryset(pk=pk)
        response_data = {}
        if business:
            serializer = self.serializer_class(business, data = request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = { 'data': serializer.data, 'message': 'Negocio actualizado correctamente' }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = { 'errors': serializer.errors, 'message' : 'Error al actualizar el negocio, información inválida' }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        response_data = { 'errors': 'No se ha encontrado el negocio', 'message' : 'El negocio no existe' }
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    

    def delete(self, request, pk):
        business = self.get_queryset(pk=pk)
        response_data = {}

        if business:
            serializer = self.serializer_class(business)
            data = serializer.data
            response_data['data'] = data
            response_data['message'] = 'Negocio eliminado correctamente'
            business.delete()
            return Response(response_data, status=status.HTTP_200_OK)
        
        response_data['errors'] = 'No se ha encontrado el negocio'
        response_data['message'] = 'El negocio no existe'
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            