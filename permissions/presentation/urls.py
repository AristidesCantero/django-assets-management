from django.urls import path
from permissions.presentation.api import permission_api, groups_api, group_user_api
urlpatterns = [
    # Permissions API
    path('permissions/', permission_api.PermissionListAPIView.as_view(), name='permission-list'),
    path('permissions/<int:pk>/', permission_api.PermissionDetailAPIView.as_view(), name='permission-detail'),

    # Groups API
    path('groups/', groups_api.GroupListAPIView.as_view(), name='group-list'),
    path('groups/<int:pk>/', groups_api.GroupDetailAPIView.as_view(), name='group-detail'),

    # User Business Permissions API
    path('user-permissions/<int:user_id>/', group_user_api.GroupUserAPIView.as_view(), name='user-permissions'),
]