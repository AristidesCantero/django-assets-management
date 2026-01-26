from django.urls import path, include
from locations.api.business_api import *
from locations.api.internal_location_api import *

urlpatterns = [
    path('businesses',BusinessListAPIView.as_view(),name='business_list_api'),
    path('business/<int:pk>',BusinessAPIView.as_view(),name='business_detail_api'),
    path('internallocations',InternalLocationAPI.as_view(),name='internal_location_list_api'),
    path('internallocation/<int:pk>',InternalLocationAPI.as_view(),name='internal_location_detail_api'),
]
