from django.urls import path

from users.api.api import *

urlpatterns = [
    path('usuario/',user_api_view, name='usuario_api'),
    path('usuario/<int:pk>/',user_detail_api_view, name='usuario_detail_api_view'),
]
