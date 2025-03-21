from django.urls import path, include
from . import views

urlpatterns = [
    path('business',views.BusinessAPIView.as_view()),
    path('business/<int:pk>',views.BusinessDetailAPIView.as_view()),
    path('headquarters',views.HeadquartersAPIView.as_view()),
    path('headquarters/<int:pk>',views.HeadquartersDetailAPIView.as_view()),
    path('internal-location',views.InternalLocationAPIView.as_view()),
    path('internal-location/<int:pk>',views.InternalLocationAPIView.as_view()),
]
