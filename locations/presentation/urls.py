from django.urls import path, include
from locations.presentation.api.business_api import *
from locations.presentation.api.internal_location_api import *
from locations.presentation.api.headquarter_api import * 

urlpatterns = [
   # business
    path('businesses/',BusinessListAPIView.as_view(),name='business_list_api'),
    path('business/<int:business_id>/',BusinessAPIView.as_view(),name='business_detail_api'),
    #Headquarters
    path('headquarters/', HeadquarterListAPIView.as_view(), name='headquarter_list_api'),
    path('headquarters/<int:pk>', HeadquarterListAPIView.as_view(), name='headquarter_list_api_business'),
    path('headquarter/<int:pk>/', HeadquarterAPIView.as_view(), name='headquarter_detail_api'),
    #InternalLocations
    path('internallocations/',InternalLocationListAPIView.as_view(),name='internal_location_list_api'),
    path('internallocation/<int:pk>/',InternalLocationAPIView.as_view(),name='internal_location_detail_api'),
]
