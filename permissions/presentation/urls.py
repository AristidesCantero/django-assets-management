from django.urls import path
from permissions.presentation.api import *


urlpatterns = [
    path('fpermission/<int:pk>/', ForbiddenGroupPermissionsDetailAPI.as_view(), name='forbidden-group-permissions-detail'),
    path('fpermissions/', ForbiddenGroupPermissionsListCreateAPI.as_view(), name='forbidden-group-permissions-list-create'),
]