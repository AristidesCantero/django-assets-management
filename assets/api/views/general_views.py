from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
from assets.domain.models import *
from assets.api.serializers.general_serializers import *
from rest_framework import generics
from rest_framework.decorators import authentication_classes, permission_classes



# Create your views here.
#las vistas definen el comportamiento de la API

##estas lineas permiten omitir la autenticacion y permisos para defs
#@authentication_classes([])
#@permission_classes([])

class AssetsUnitListAPIView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return Asset.objects.all()
    
    serializer_class = AssetSerializer

class AssetsAPIView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

class AssetAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


