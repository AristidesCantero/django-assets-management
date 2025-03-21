from django.shortcuts import render, redirect
from rest_framework import generics
from components.models import *
from components.serializers import *

# Create your views here.

#Assets APIs
class AssetSystemAPIView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = AssetSystem.objects.all()
    serializer_class = AssetSystemSerializer

class AssetSystemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = AssetSystem.objects.all()
    serializer_class = AssetSystemSerializer


#Subsystem APIs
class SubsystemComponentAPIView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = SubsystemComponent.objects.all()
    serializer_class = SubsystemComponentSerializer


class SubsystemComponentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = SubsystemComponent.objects.all()
    serializer_class = SubsystemComponentSerializer


#Minimum Component APIs
class MinimumComponentAPIView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = MinimumComponent.objects.all()
    serializer_class = MinimumComponentSerializer


class MinimumComponentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = MinimumComponent.objects.all()
    serializer_class = MinimumComponentSerializer