from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.presentation.serializers.user_serializer import UserSerializer, UserListSerializer, UserTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from permissions.domain.permissions import *
from permissions.domain.authentication import CookieJWTAuthentication
from users.domain.models import User
from django.db import connection
from django.conf import settings


def sqlQuery(query: str, params: tuple = ()):
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return results


def path_has_primary_key(path: str) -> bool:
    segments = path.strip('/').split('/')
    primary_key = segments[-1]
    return primary_key if primary_key.isdigit() else None




#User management by business
class UserListAPIView(ListCreateAPIView):
    serializer_class = UserListSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissionsToCheckUsers]  #use function get_permission to customize
    http_method_names = ["get", "post"]


    #funcion para realizar la consulta sql y recibir un diccionario por cada fila en donde las llaves son los nombres de las columnas
    


    def get_queryset(self, user: User = None):
        if user.is_superuser:
            return User.objects.all()
        return User.objects.users_allowed_to_user(request=self.request)   
    

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            self.check_object_permissions(request,user)
            response_data = {}               
            queryset = self.get_queryset(user=user)
            response_data['data'] = self.serializer_class(queryset, many=True).data
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        self.check_object_permissions(request,user)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissionsToCheckUsers]
    http_method_names = ["get", "patch", "delete"]
    
    
    def get_queryset(self, pk):
        user_data = User.objects.user_is_allowed_to_check_user(request=self.request, consulted_user_id=pk)
        if not user_data["exists"] or not user_data['user']:
            raise User.DoesNotExist
        return user_data["user"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, pk, *args, **kwargs):
        try:
            user = self.get_queryset(pk=pk)
            response_data = {
                'data': self.serializer_class(user,context={'request': request}).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            print('a user has not been found')
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
 
    def patch(self, request, pk, *args, **kwargs):
        try:
            user = self.get_queryset(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            
            serializer.update(user, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        try:
            print(pk)
            user = self.get_queryset(pk=pk)
            user_serializer_data = self.serializer_class(user, context={'request': request}).data
            user.delete()
            return Response({'detail': 'User has been deleted successfully.', "data": user_serializer_data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)

 #   def get_permissions(self):
 #        match self.request.method:
 #           case 'GET':
 #               self.permission_classes = [adminPermissionInModelsManager]
 #           case 'POST':
 #               self.permission_classes = [IsAdminUser]
 #           case 'PUT':
 #               self.permission_classes = [IsAdminUser]
 #           case 'DELETE':
 #               self.permission_classes = [IsAdminUser]
 #        return super().get_permissions()
    







class CustomizedTokenObtainPairView(TokenObtainPairView):
    """
    Override the default TokenObtainPairView to set access/refresh tokens as HttpOnly cookies.
    """
    def post(self, request, *args, **kwargs):
        # Get tokens using the default TokenObtainPairView logic
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
 
        # Extract tokens from the serializer
        access_token = serializer.validated_data["access"]
        refresh_token = serializer.validated_data["refresh"]
 
        # Create a response (no tokens in the body)
        response = Response({"detail": "Tokens generated successfully"})
 
        # Set access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # Prevent JavaScript access
            secure=not settings.DEBUG,  # Use HTTPS in production
            samesite="Strict",  # Mitigate CSRF
            max_age=15 * 60,  # 15 minutes (matches ACCESS_TOKEN_LIFETIME)
            path="/",  # Cookie sent to all routes
        )
 
        # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Strict",
            max_age=24 * 60 * 60,  # 1 day (matches REFRESH_TOKEN_LIFETIME)
            path="/",
        )
 
        return response


class CustomizedTokenRefreshView(TokenRefreshView):
    """
    Override TokenRefreshView to read the refresh token from a cookie and set a new access token cookie.
    """
    def post(self, request, *args, **kwargs):
        # Extract refresh token from the "refresh_token" cookie
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies"},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        # Use the refresh token to get a new access token
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
 
        # Extract the new access token
        new_access_token = serializer.validated_data["access"]
 
        # Create a response and set the new access token cookie
        response = Response({"detail": "Token refreshed successfully"})
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Strict",
            max_age=15 * 60,  # 15 minutes
            path="/",
        )
 
        return response