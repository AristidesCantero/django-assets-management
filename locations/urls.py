from django.urls import path, include
from locations.api.business_api import *
from locations.api.internal_location_api import *
from locations.api.headquarter_api import * 

urlpatterns = [
    path('businesses',BusinessListAPIView.as_view(),name='business_list_api'),
    path('business/<int:pk>',BusinessAPIView.as_view(),name='business_detail_api'),
    path('headquarters', HeadquarterListAPIView.as_view(), name='headquarter_list_api'),
    path('headquarters/<int:pk>', HeadquarterAPIView.as_view(), name='headquarter_detail_api'),
    path('internallocations',InternalLocationListAPIView.as_view(),name='internal_location_list_api'),
    path('internallocation/<int:pk>',InternalLocationAPIView.as_view(),name='internal_location_detail_api'),
]
