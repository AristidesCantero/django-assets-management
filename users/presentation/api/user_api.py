from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.presentation.serializers.user_serializer import UserSerializer, UserListSerializer, UserTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from permissions.domain.permissions import *
from users.domain.models import User
from django.db import connection


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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
    serializer_class = UserTokenObtainPairSerializer


class CustomizedTokenRefreshView(TokenRefreshView):
    serializer_class = UserTokenObtainPairSerializer