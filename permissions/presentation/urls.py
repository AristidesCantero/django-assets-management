from django.urls import path
from permissions.presentation.api import permission_api, business_membership_api
urlpatterns = [
    # Permissions API
    path('permissions/', permission_api.PermissionListAPIView.as_view(), name='permission-list'),
    path('permissions/<int:permission_id>/', permission_api.PermissionDetailAPIView.as_view(), name='permission-detail'),

    # User Business Permissions API
    path('businesses/<int:business_id>/memberships/', business_membership_api.BusinessMembershipListCreateAPIView.as_view(), name='business-membership-list'),
    path('businesses/<int:business_id>/memberships/<int:user_id>/', business_membership_api.BusinessMembershipDetailAPIView.as_view(), name='business-membership-detail'),

]