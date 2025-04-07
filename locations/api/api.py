from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from locations.models import Headquarters, Business, InternalLocation
from locations.api.serializers import *
# Create your views here.

@api_view(['GET','POST'])
def business_api_view(request):
        #GET to recieve all the businesses
        if request.method == 'GET':
             businesses = Business.objects.all().values('id','name','tin','utr')
             businesses_serializer = BusinessListSerializer(businesses, many=True)
             return Response(businesses_serializer.data, status=status.HTTP_200_OK)
        #POST to create a new business
        if request.method == 'POST':
            business_serializer = BusinessCheckSerializer(data = request.data)
            if business_serializer.is_valid():
                business_serializer.save()
                return Response(business_serializer.data, status=status.HTTP_201_CREATED)
            return Response(business_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message':'La solicitud solo acepta GET y POST, formato incorrecto'}, status = status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PUT','DELETE'])
def business_detail_api_view(request, pk=None):
    business = Business.objects.filter(id=pk).first()

    if business:
        #GET to get the business by id
        if request.method == 'GET':
            business_serializer = BusinessCheckSerializer(business)
            return Response(business_serializer.data, status=status.HTTP_200_OK)
        
        #PUT to update the business by id
        elif request.method == 'PUT':
            business_serializer = BusinessCheckSerializer(business, data = request.data)
            if business_serializer.is_valid():
                business_serializer.save()
                return Response(business_serializer.data, status=status.HTTP_200_OK)
            return Response(business_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        #DELETE to delete the business by id
        elif request.method == 'DELETE':
            business_serializer = BusinessCheckSerializer(business)
            data = business_serializer.data
            business.delete()
            return Response(data, status=status.HTTP_200_OK)
        return Response({'message':'La solicitud ha sido incorrecta'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message':'No se ha encontrado el negocio'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST'])
def headquarters_api_view(request):
        
        #GET to recieve all the headquarters
        if request.method == 'GET':
            headquarters = Headquarters.objects.all().values('id', 'name', 'address', 'phone', 'business_key')
            headquarters_serializer = HeadquartersListSerializer(headquarters, many=True)
            return Response(headquarters_serializer.data, status=status.HTTP_200_OK) 
        #POST to create a new headquarter
        if request.method == 'POST':
            headquarters_serializer = HeadquartersCheckSerializer(data = request.data)
            if headquarters_serializer.is_valid():
                headquarters_serializer.save()
                return Response(headquarters_serializer.data, status=status.HTTP_201_CREATED)
            return Response(headquarters_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message':'La solicitud no tiene un formato válido'}, status=status.HTTP_400_BAD_REQUEST)
    
    
#GET to recieve all the headquarters of a business
@api_view(['GET'])
def headquarters_by_business_api_view(request, pk=None):
    headquarters = Headquarters.objects.filter(business_key=pk).values('id', 'name', 'address', 'phone', 'business_key')
    headquarters_serializer = HeadquartersListSerializer(headquarters, many=True)
    return Response(headquarters_serializer.data, status=status.HTTP_200_OK)
    #queryset



@api_view(['GET','PUT','DELETE'])
def headquarters_detail_api_view(request, pk=None):
    headquarter = Headquarters.objects.filter(id=pk).first()

    if headquarter:
        #GET to get the headquarter by id
        if request.method == 'GET':
            headquarters_serializer = HeadquartersCheckSerializer(headquarter)
            return Response(headquarters_serializer.data, status=status.HTTP_200_OK)
        
        #PUT to update the headquarter by id
        elif request.method == 'PUT':
            headquarters_serializer = HeadquartersCheckSerializer(headquarter, data = request.data)
            if headquarters_serializer.is_valid():
                headquarters_serializer.save()
                return Response(headquarters_serializer.data, status=status.HTTP_200_OK)
            return Response(headquarters_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        #DELETE to delete the headquarter by id
        elif request.method == 'DELETE':
            data = headquarter.data
            headquarter.delete()
            return Response({'message':'sede Eliminada', 'data':data}, status=status.HTTP_200_OK)
    return Response({'message':'No se ha encontrado la sede'}, status=status.HTTP_400_BAD_REQUEST)



#Business APIs
class BusinessAPIView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

class BusinessDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer


# #Headquarters APIs
# class HeadquartersAPIView(generics.ListCreateAPIView):
#     authentication_classes = []
#     permission_classes = []
#     queryset = Headquarters.objects.all()
#     serializer_class = HeadquartersSerializer

# class HeadquartersDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     authentication_classes = []
#     permission_classes = []
#     queryset = Headquarters.objects.all()
#     serializer_class = HeadquartersSerializer


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


