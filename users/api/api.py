from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import permission_classes, authentication_classes
from users.api.serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from permissions.permissions import *
from users.models import User
from django.contrib.auth.models import Permission, Group
from django.db import connection
from permissions.backends import BusinessPermissionBackend


def sqlQuery(query: str, params: tuple = ()):
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return results



class GroupAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionsToCheckGroups]
    queryset = Group.objects.all()
    http_method_names = ['get', 'patch', 'delete']
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, pk, *args, **kwargs):
        try:
            group = Group.objects.get(pk=pk)
            #self.check_object_permissions(request,group)

            response_data = {
                'data': self.serializer_class(group,context={'request': request}).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'detail': 'Group has not been found.'}, status=status.HTTP_404_NOT_FOUND)
 
    
    def patch(self, request, pk, *args, **kwargs):
        try:
            group = Group.objects.get(pk=pk)
            self.check_object_permissions(request,group)
        except Group.DoesNotExist:
            return Response({'detail': 'Group has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(group, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.update(group, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        try:
            group = Group.objects.get(pk=kwargs['pk'])
            group_serializer_data = self.serializer_class(group).data
            group.delete()
            return Response({'detail': 'Group has been deleted successfully.', "data": group_serializer_data}, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'detail': 'Group has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        

class GroupListAPIView(ListCreateAPIView):
    serializer_class = GroupListSerializer
    queryset = serializer_class.Meta.model.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionsToCheckGroups]


    def groupSqlQuery(self, user: User = None):
        return Group.objects.all()


    def get(self, request, *args, **kwargs):
        try:
            groups = Group.objects.all()
            response_data = {}
            response_data['data'] = self.serializer_class(groups, many=True).data
            return Response(response_data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'detail': 'Group has not been found.'}, status=status.HTTP_404_NOT_FOUND)

    
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





#Default user API views
class UserListAPIView(ListCreateAPIView):
    serializer_class = UserListSerializer
    queryset = serializer_class.Meta.model.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionsToCheckUsers]  #use function get_permission to customize
    http_method_names = ["get", "post"]


    #funcion para realizar la consulta sql y recibir un diccionario por cada fila en donde las llaves son los nombres de las columnas
    

    def usersSqlQuery(self, user: User = None):
        if user is None:
            return None
        
        user_businesses = sqlQuery(query = "SELECT distinct business_key_id from permissions_userbusinesspermission where user_key_id = %s" % user.id)
        user_businesses = [str(x['business_key_id']) for x in user_businesses]
        users_ids = []
        if user_businesses:
            users_ids = sqlQuery(query = "SELECT DISTINCT user_key_id FROM permissions_userbusinesspermission WHERE business_key_id IN (%s)" % ",".join(user_businesses) )

        users_ids = [str(x['user_key_id']) for x in users_ids] 
        users = []
        if users_ids:
            users = User.objects.filter(id__in = users_ids)
        
        return users

    def get_queryset(self, user: User = None):
        if not user:
            return User.objects.all()
        return self.usersSqlQuery(user=user)    
    

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
    queryset = User.objects.all()
    http_method_names = ["get", "patch"]
    
    


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            response_data = {
                'data': self.serializer_class(user,context={'request': request}).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
 
    
    def patch(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            self.check_object_permissions(request,user)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(user, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.update(user, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=kwargs['pk'])
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