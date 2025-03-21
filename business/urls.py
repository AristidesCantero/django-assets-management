from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('assets/',views.AssetsAPIView.as_view()),
    path('asset/<int:pk>',views.AssetAPIView.as_view()),
    path('',views.businessHome, name="businessHome"),
    path('components/<str:pk>/',views.businessComponents,name="businessComponents"),
]