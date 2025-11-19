from django.urls import path

from permissions.api import AdminPermissionView, AdminPermissionListView

urlpatterns = [
    path('permissions/',AdminPermissionListView.as_view(), name='usuario_api'),
    path('permission/<int:pk>/',AdminPermissionView.as_view(), name='usuario_detail_api_view'),
]