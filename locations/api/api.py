from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from locations.models import Headquarters, Business, InternalLocation
from locations.api.serializers import *
# Create your views here.

@api_view(['GET','POST'])
def headquarters_api_view(request):
    # try:
        if request.method == 'GET':
            headquarters = Headquarters.objects.all().values('id', 'name', 'address', 'phone', 'business_key')
            headquarters_serializer = HeadquartersListSerializer(headquarters, many=True)
            return Response(headquarters_serializer.data, status=status.HTTP_200_OK) 
        
        if request.method == 'POST':
            headquarters_serializer = HeadquartersCheckSerializer(data = request.data)
            if headquarters_serializer.is_valid():
                headquarters_serializer.save()
                return Response(headquarters_serializer.data, status=status.HTTP_201_CREATED)
            return Response(headquarters_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message':'La solicitud no tiene un formato válido'}, status=status.HTTP_400_BAD_REQUEST)
    # except Exception as e:
    #     return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def headquarters_by_business_api_view(request, pk=None):
    headquarters = Headquarters.objects.filter(business_key=pk).values('id', 'name', 'address', 'phone', 'business_key')
    headquarters_serializer = HeadquartersListSerializer(headquarters, many=True)
    return Response(headquarters_serializer.data, status=status.HTTP_200_OK)
    #queryset

@api_view(['GET','PUT','DELETE'])
def headquarters_detail_api_view(request, pk=None):
    headquarters = Headquarters.objects.filter(id=pk).first()

    if headquarters:
        if request.method == 'GET':
            headquarters_serializer = HeadquartersCheckSerializer(headquarters)
            return Response(headquarters_serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            headquarters_serializer = HeadquartersCheckSerializer(headquarters, data = request.data)
            if headquarters_serializer.is_valid():
                headquarters_serializer.save()
                return Response(headquarters_serializer.data, status=status.HTTP_200_OK)
            return Response(headquarters_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            headquarters.delete()
            return Response({'message':'sede Eliminada'}, status=status.HTTP_200_OK)
    return Response({'message':'No se ha encontrado la sede'}, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])



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


