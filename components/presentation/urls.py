from django.urls import path, include
from . import views

urlpatterns = [
    path('asset-systems/',views.AssetSystemAPIView.as_view()),
    path('asset-system/<int:pk>',views.AssetSystemDetailAPIView.as_view()),
    path('subsystem-components/',views.SubsystemComponentAPIView.as_view()),
    path('subsystem-component/<int:pk>',views.SubsystemComponentDetailAPIView.as_view()),
    path('minimum-components/',views.MinimumComponentAPIView.as_view()),
    path('minimum-component/<int:pk>',views.MinimumComponentDetailAPIView.as_view()),
]