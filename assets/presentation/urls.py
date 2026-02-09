from django.contrib import admin
from django.urls import path, include

from assets.api.asset_api import *

urlpatterns = [
    path('assets/',AssetListAPIView.as_view()),
    path('asset/<int:pk>',AssetAPIView.as_view()),
]