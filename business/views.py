from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
from business.models import *
from business.serializers import *
from rest_framework import generics
from rest_framework.decorators import authentication_classes, permission_classes



# Create your views here.
#las vistas definen el comportamiento de la API

##estas lineas permiten omitir la autenticacion y permisos para defs
#@authentication_classes([])
#@permission_classes([])
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


def businessHome(request):
    Assets = Asset.objects.all()
    context = {'Assets': Assets}
    return render('business/information/business_assets.html',context)



def businessComponents(request, pk):

    asset = Asset.objects.get(id=pk)
    Components = asset.component_set.all().filter(asset_key=pk)
    context = {'Components': Components}
    return render('business/information/business_components.html',context)

