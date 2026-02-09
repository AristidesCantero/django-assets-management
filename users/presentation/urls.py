from django.urls import path

from users.api.user_api import *
from users.api.group_api import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('usuarios/',UserListAPIView.as_view(), name='usuario_api'),
    path('usuario/<int:pk>/',UserAPIView.as_view(), name='usuario_detail_api_view'),
    path('grupos/',GroupListAPIView.as_view(), name='group_api'),
    path('grupo/<int:pk>/',GroupAPIView.as_view(), name='group_detail_api_view'),
    path('token/', CustomizedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
