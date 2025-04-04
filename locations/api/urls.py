from django.urls import path, include
from locations.api.api import *
from locations.api.views.general_views import InternalLocationListAPIView

urlpatterns = [
    path('businesses',BusinessAPIView.as_view()),
    path('business/<int:pk>',BusinessDetailAPIView.as_view()),
    path('headquarters',headquarters_api_view,name='headquarters_api_view'),
    path('headquarters/<int:pk>',headquarters_by_business_api_view,name='headquarters_by_business_api_view'),
    path('headquarter/<int:pk>',headquarters_detail_api_view,name='headquarters_detail_api_view'),
    path('internal_location',InternalLocationListAPIView.as_view(),name='internal_location_list_api_view'),

    # path('headquarters',HeadquartersAPIView.as_view()),
    # path('headquarters/<int:pk>',HeadquartersDetailAPIView.as_view()),
    # path('internal-location',InternalLocationAPIView.as_view()),
    # path('internal-location/<int:pk>',InternalLocationAPIView.as_view()),
]
