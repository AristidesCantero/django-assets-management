from django.urls import path

from users.api.api import *

urlpatterns = [
    path('usuarios/',UserListAPIView.as_view(), name='usuario_api'),
    path('usuario/<int:pk>/',UserAPIView.as_view(), name='usuario_detail_api_view'),
    path('admin_usuarios/',AdminUserListAPIView.as_view(), name='admin_usuario_api'),
    path('admin_usuario/<int:pk>',AdminUserAPIView.as_view(), name='admin_usuario_detail_api_view'),
    path('grupos/',GroupListAPIView.as_view(), name='group_api'),
    path('grupo/<int:pk>/',GroupAPIView.as_view(), name='group_detail_api_view'),
    path('token/', CustomizedTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
