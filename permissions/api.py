from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from permissions.serializers import *
from permissions.models import AdminPermission, ManagerPermission, BusinessPermission


class AdminPermissionView(RetrieveUpdateDestroyAPIView):
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAdminUser]
    serializer_class = AdminPermissionSerializer
    queryset = AdminPermission.objects.all()

class AdminPermissionListView(ListCreateAPIView):
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAdminUser]
    serializer_class = AdminPermissionListSerializer
    queryset = AdminPermission.objects.all()
    