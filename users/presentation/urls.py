from django.urls import path

from users.presentation.api.group_api import *
from users.presentation.api.user_api import *
from users.presentation.api.session_token_api import *


urlpatterns = [
    path('prueba/',MailTesting.as_view(), name='test_mail'),
    path('registro/',UserRegisterAPIView.as_view(), name='usuario_api'), 
    #registro de nuevo usuario
    path('confirma/',UserRegisterConfirmationAPIView.as_view(),name="confirmacion_usuario"),
    path('empresa/<int:business_id>/usuario/<int:user_id>/',UserAPIView.as_view(), name='usuario_detail_api_view'), 
    #apis de usuario por empresa
    path('empresa/<int:business_id>/',UserListAPIView.as_view(), name='usuario_detail_api_view'),
    path('grupos/',GroupListAPIView.as_view(), name='group_api'), 
    #apis de grupos
    path('grupo/<int:pk>/',GroupAPIView.as_view(), name='group_detail_api_view'),
    #apis de sesion de usuario
    path('token/', CustomizedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomizedTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', CustomizedTokenBlackListLogout.as_view(), name='logout'),
    #apis de invitacion 
    path('send-invitation/', InvitationAPIView.as_view(), name='send-invitation'),
    path('accept-invitation/', InvitationAcceptAPIView.as_view(), name='accept-invitation'),
]
