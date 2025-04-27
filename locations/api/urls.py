from django.urls import path, include
from locations.api.api import *
from locations.api.views.general_views import InternalLocationListAPIView, InternalLocationDetailAPIView

urlpatterns = [
    path('businesses',BusinessListCreateAPIView.as_view(),name='business_api_view'),
    path('business/<int:pk>',BusinessRetrieveUpdateDestroyAPIView.as_view(),name='business_detail_api_view'),
    path('headquarters',headquarters_api_view,name='headquarters_api_view'),
    path('headquarters/<int:pk>',headquarters_by_business_api_view,name='headquarters_by_business_api_view'),
    path('headquarter/<int:pk>',headquarters_detail_api_view,name='headquarters_detail_api_view'),
    path('internal/create',InternalLocationDetailAPIView.as_view(), name='headquarter_create'),
    path('internal',InternalLocationListAPIView.as_view(),name='internal_location_list_api_view'),
    path('<path:resource>', not_found_api_view, name='not_found_api_view'),
]
