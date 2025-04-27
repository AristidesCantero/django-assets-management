from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from locations.models import Headquarters, Business, InternalLocation
from locations.api.serializers import *
# Create your views here.


@api_view(['GET','PUT','DELETE'])
def business_detail_api_view(request, pk=None):
    business = Business.objects.filter(id=pk).first()
    response_data = {}

    if business:
        #GET to get the business by id
        if request.method == 'GET':
            business_serializer = BusinessCheckSerializer(business)
            response_data['data'] = business_serializer.data
            return Response(response_data, status=status.HTTP_200_OK)
        
        #PUT to update the business by id
        elif request.method == 'PUT':
            business_serializer = BusinessCheckSerializer(business, data = request.data)
            if business_serializer.is_valid():
                business_serializer.save()
                response_data['data'] = business_serializer.data
                response_data['message'] = 'Negocio actualizado correctamente'
                return Response(response_data, status=status.HTTP_200_OK)
            response_data['errors'] = business_serializer.errors
            response_data['message'] = 'Error al actualizar el negocio'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        #DELETE to delete the business by id
        elif request.method == 'DELETE':
            business_serializer = BusinessCheckSerializer(business)
            data = business_serializer.data
            response_data['data'] = data
            response_data['message'] = 'Negocio eliminado correctamente'
            business.delete()
            return Response(response_data, status=status.HTTP_200_OK)
        response_data['errors'] = 'Solicitud no válida'
        response_data['message'] = 'La solicitud no tiene un formato válido'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    response_data['errors'] = 'No se ha encontrado el negocio'
    response_data['message'] = 'El negocio no existe'
    return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class BusinessListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BusinessCheckSerializer

    def get_queryset(self, pk=None):
        if pk is None:
            return BusinessCheckSerializer.Meta.model.objects.all()
        return self.serializer_class.Meta.model.objects.filter(id=pk).first()


    def get(self, pk=None):
        query = self.get_queryset().values('id','name','tin','utr')
        context = {
            'data':query
        }
        return Response(context, status=status.HTTP_200_OK)
    
    def post(self, request):
        business_serializer = BusinessCheckSerializer(data = request.data)
        response_data = {}

        if business_serializer.is_valid():
            business_serializer.save()
            response_data['data'] = business_serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data['errors'] = business_serializer.errors
        response_data['message'] = 'Error al crear el negocio'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class BusinessRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessCheckSerializer

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
        
    

    def put(self, request, pk=None):
        business = self.get_queryset(pk=pk)
        response_data = {}
        if business:
            business_serializer = self.serializer_class(business, data = request.data)
            if business_serializer.is_valid():
                business_serializer.save()
                response_data['data'] = business_serializer.data
                response_data['message'] = 'Negocio actualizado correctamente'
                return Response(response_data, status=status.HTTP_200_OK)
            
            response_data['errors'] = business_serializer.errors
            response_data['message'] = 'Error al actualizar el negocio'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        response_data['errors'] = 'No se ha encontrado el negocio'
        response_data['message'] = 'El negocio no existe'
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk=None):
        business = self.get_queryset(pk=pk)
        response_data = {}

        if business:
            business_serializer = BusinessCheckSerializer(business)
            data = business_serializer.data
            response_data['data'] = data
            response_data['message'] = 'Negocio eliminado correctamente'
            business.delete()
            return Response(response_data, status=status.HTTP_200_OK)
        
        response_data['errors'] = 'No se ha encontrado el negocio'
        response_data['message'] = 'El negocio no existe'
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
        

@api_view(['GET','POST'])
def headquarters_api_view(request):
        
        response_data = {}
        #GET to recieve all the headquarters
        if request.method == 'GET':
            headquarters = Headquarters.objects.all().values('id', 'name', 'address', 'phone', 'business_key')
            headquarters_serializer = HeadquartersListSerializer(headquarters, many=True)
            response_data['data'] = headquarters_serializer.data
            return Response(response_data, status=status.HTTP_200_OK) 
        #POST to create a new headquarter
        if request.method == 'POST':
            headquarters_serializer = HeadquartersCheckSerializer(data = request.data)
            if headquarters_serializer.is_valid():
                headquarters_serializer.save()
                response_data['data'] = headquarters_serializer.data
                response_data['message'] = 'Sede creada correctamente'
                return Response(response_data, status=status.HTTP_201_CREATED)
            response_data['errors'] = headquarters_serializer.errors
            response_data['message'] = 'Error al crear la sede'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        response_data['errors'] = 'La solicitud no tiene un formato válido'
        response_data['message'] = 'No se ha logrado la solicitud'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    
#GET to recieve all the headquarters of a business
@api_view(['GET'])
def headquarters_by_business_api_view(request, pk=None):
    response_data = {}
    headquarters = Headquarters.objects.filter(business_key=pk).values('id', 'name', 'address', 'phone', 'business_key')
    headquarters_serializer = HeadquartersListSerializer(headquarters, many=True)
    response_data['data'] = headquarters_serializer.data
    return Response(response_data, status=status.HTTP_200_OK)
    #queryset



@api_view(['GET','PUT','DELETE'])
def headquarters_detail_api_view(request, pk=None):
    headquarter = Headquarters.objects.filter(id=pk).first()
    response_data = {}

    if headquarter:
        #GET to get the headquarter by id
        if request.method == 'GET':
            headquarters_serializer = HeadquartersCheckSerializer(headquarter)
            response_data['data'] = headquarters_serializer.data 
            return Response(response_data, status=status.HTTP_200_OK)
        
        #PUT to update the headquarter by id
        elif request.method == 'PUT':
            headquarters_serializer = HeadquartersUpdateSerializer(headquarter, data = request.data)
            if headquarters_serializer.is_valid():
                headquarters_serializer.save()
                response_data['data'] = headquarters_serializer.data
                response_data['message'] = 'Sede actualizada correctamente'
                return Response(response_data, status=status.HTTP_200_OK)
            response_data['errors'] = headquarters_serializer.errors
            response_data['message'] = 'Error al actualizar la sede'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        #DELETE to delete the headquarter by id
        elif request.method == 'DELETE':
            headquarters_serializer = HeadquartersCheckSerializer(headquarter)
            data = headquarters_serializer.data
            response_data['data'] = data
            response_data['message'] = 'Sede eliminada correctamente'
            headquarter.delete()
            return Response(response_data, status=status.HTTP_200_OK)
    response_data['errors'] = 'No se ha encontrado la sede'
    response_data['message'] = 'La solicitud ha sido incorrecta'
    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET','POST'])
def internal_locations_api_view(request):
    response_data = {}
    #GET to recieve all the internal locations
    if request.method == 'GET':

        internal_locations = InternalLocation.objects.all().values('id', 'name', 'address', 'phone', 'headquarter_key')
        internal_locations_serializer = InternalLocationListSerializer(internal_locations, many=True)
        response_data['data'] = internal_locations_serializer.data
        return Response(response_data, status=status.HTTP_200_OK) 
    
    #POST to create a new internal location
    if request.method == 'POST':

        internal_location_serializer = InternalLocationCheckSerializer(data = request.data)
        if internal_location_serializer.is_valid():

            internal_location_serializer.save()
            response_data['data'] = internal_location_serializer.data
            response_data['message'] = 'Ubicación interna creada correctamente'
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        response_data['errors'] = internal_location_serializer.errors
        response_data['message'] = 'No se ha logrado crear la ubicación interna'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    response_data['errors'] = 'La solicitud no tiene un formato válido'
    response_data['message'] = 'No se ha logrado la solicitud'
    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET','PUT','DELETE'])
def internal_location_detail_api_view(request, pk=None):
    internal_location = InternalLocation.objects.filter(id=pk).first()
    response_data = {}

    if internal_location:
        if request.method == 'GET':
            internal_location_serializer = InternalLocationCheckSerializer(internal_location)
            response_data['data'] = internal_location_serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)

        if request.method == 'PUT':
            internal_location_serializer = InternalLocationUpdateSerializer(internal_location, data = request.data)
            if internal_location_serializer.is_valid():
                internal_location_serializer.save()
                response_data['data'] = internal_location_serializer.data
                response_data['message'] = 'Locación actualizada exitosamente'
                return Response(response_data,status = status.HTTP_202_ACCEPTED)
            response_data['errors'] = internal_location_serializer.errors
            response_data['message'] = 'No se ha podido actualizar la Locación'
            return Response(response_data,status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'DELETE':
            internal_location_serializer = InternalLocationCheckSerializer(internal_location)
            response_data['data'] = internal_location_serializer.data
            response_data['message'] = f'Locacion {internal_location_serializer.data.name} borrada exitosamente'
            internal_location.delete()
            Response(response_data, status=status.HTTP_200_OK)
        
        response_data['errors'] = {'method': 'La solicitud no es válida'}
        return Response(response_data,status=status.HTTP_400_BAD_REQUEST)
    
    response_data['errors'] = {'location': 'El elemento no se ha encontrado'}
    return Response(response_data, status=status.HTTP_404_NOT_FOUND) 




@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def not_found_api_view(request, *args, **kwargs):
        response_data = {
            'errors': 'La URL solicitada no existe',
            'message': 'Por favor, verifique la URL y vuelva a intentarlo'
        }
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)

# #Internal Location APIs
# class InternalLocationAPIView(generics.ListCreateAPIView):
#     authentication_classes = []
#     permission_classes = []
#     queryset = InternalLocation.objects.all()
#     serializer_class = InternalLocationSerializer

# class InternalLocationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     authentication_classes = []
#     permission_classes = []
#     queryset = InternalLocation.objects.all()
#     serializer_class = InternalLocationSerializer


