from assets.models import *
from assets.serializers.system_segregation_serializer import SystemSegregationSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from permissions.permissions import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status




class SystemSegregationAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionToCheckModel]
    serializer_class = [SystemSegregationSerializer]
    allowed_methods = ["GET", "PATCH", "DELETE"]


    def get_queryset(self):
        pass

