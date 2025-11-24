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
from permissions.models import AdminPermission



#Default user API views
class UserListAPIView(ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = serializer_class.Meta.model.objects.all()
    authentication_classes = [JWTAuthentication]
    #permission_classes = [isAdmin]

    def get_queryset(self):
        adminPermissions = AdminPermission.objects.all()
        adminUsers = [permission.user_key for permission in adminPermissions]
        users = User.objects.exclude(id__in=adminUsers)
        return users
    
    
    def get(self, request, *args, **kwargs):
        
        #token = request.auth
        #user = adminPermission.user_is_admin(token)
        #print(user.username+" with an id: "+str(user.id)+" is trying to access the user list.")

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    

    def get(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            self.check_object_permissions(request,user)
            return Response(self.serializer_class(user).data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User has not been found.'}, status=status.HTTP_404_NOT_FOUND)
 
    def post(self, request, *args, **kwargs):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get_permissions(self):
         match self.request.method:
            case 'GET':
                self.permission_classes = [adminPermissionInModelsManager]
            case 'POST':
                self.permission_classes = [IsAdminUser]
            case 'PUT':
                self.permission_classes = [IsAdminUser]
            case 'DELETE':
                self.permission_classes = [IsAdminUser]
         return super().get_permissions()
    

#Admin users API views
class AdminUserAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserAdminSerializer
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
    serializer_class = UserAdminListSerializer
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [isAdmin]

    def get_queryset(self):
        users = self.serializer_class.Meta.model.objects.all()
        admin_users = [user for user in users if AdminPermission.objects.filter(user_key=user.id).exists()]
        return admin_users

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
        
class CustomizedTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer