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
from permissions.backends import BusinessPermissionBackend


class GroupAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [isAdmin]
    queryset = Group.objects.all()
    
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
 
    
    def put(self, request, pk, *args, **kwargs):
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
    permission_classes = [isAdmin]

    def get(self, request, *args, **kwargs):
        try:
            groups = Group.objects.all()
            response_data = {}
            response_data['data'] = self.serializer_class(groups, many=True).data
            return Response(response_data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'detail': 'Group has not been found.'}, status=status.HTTP_404_NOT_FOUND)

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)




#Default user API views
class UserListAPIView(ListCreateAPIView):
    serializer_class = UserListSerializer
    queryset = serializer_class.Meta.model.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionsOverTheModel]

    def get_queryset(self):
        users = User.objects.all()
        return users
    
    
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            user_has_permission = user.has_perm('users.view_user', obj = user)
            print("user_has_permission:", user_has_permission)

            #self.check_object_permissions(request,user)
            users = User.objects.all()


            response_data = {}
            response_data['data'] = self.serializer_class(users, many=True).data
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionOverThisBusiness]#[IsAdminUser]
    queryset = User.objects.all()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            self.check_object_permissions(request,user)

            response_data = {
                'data': self.serializer_class(user,context={'request': request}).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
 
    
    def put(self, request, pk, *args, **kwargs):
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
    



#Admin users API views
class AdminUserAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    #permission_classes = [isAdmin]#, adminPermissionInModelsManager]
    queryset = User.objects.all()


    def get(self, request, pk, *args, **kwargs):
        user = self.find_admin_user(pk)
        if not user:
            return Response({'detail': 'Admin user has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, *args, **kwargs):
        user = self.find_admin_user(pk)
        if not user:
            return Response({'detail': 'Admin user has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(user, data=request.data, partial=True)

        if serializer.is_valid():
            print('serializer data:', serializer.validated_data)
            serializer.update(user, request.data)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

        
    def find_admin_user(self, pk) -> User | None:
        try:
            user = User.objects.get(pk=pk)
            if not AdminPermission.objects.filter(user_key=user.id).exists():
                return None
            return user
        except User.DoesNotExist:
            return None
    

    
    def get_permissions(self):
        match self.request.method:
            case 'GET':
                self.permission_classes = [adminPermissionInModelsManager]    
            case 'POST':
                self.permission_classes = [isAdmin]
            case 'PUT':
                self.permission_classes = [isAdmin]
            case 'DELETE':
                self.permission_classes = [isAdmin]
        return super().get_permissions()
    

class AdminUserListAPIView(ListCreateAPIView):
    serializer_class = UserListSerializer
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [isAdmin]

    def get_queryset(self):
        users = self.serializer_class.Meta.model.objects.all()
        return users

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
        




class CustomizedTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer