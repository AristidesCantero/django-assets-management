from django.contrib import admin
from django.urls import path, include

from .api.views import general_views

urlpatterns = [
    path('assets/',general_views.AssetsAPIView.as_view()),
    path('asset/<int:pk>',general_views.AssetAPIView.as_view()),
]