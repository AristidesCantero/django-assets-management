from django.shortcuts import render, redirect
from rest_framework import generics
from locations.models import *
from locations.serializers import *
# Create your views here.


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


#Headquarters APIs
class HeadquartersAPIView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = Headquarters.objects.all()
    serializer_class = HeadquartersSerializer

class HeadquartersDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = Headquarters.objects.all()
    serializer_class = HeadquartersSerializer


#Internal Location APIs
class InternalLocationAPIView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = InternalLocation.objects.all()
    serializer_class = InternalLocationSerializer

class InternalLocationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = InternalLocation.objects.all()
    serializer_class = InternalLocationSerializer


