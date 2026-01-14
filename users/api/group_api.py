from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from permissions.permissions import permissionsToCheckGroups
from users.serializers.group_serializer import GroupSerializer, GroupListSerializer
from django.contrib.auth.models import Group
from users.models import User
from django.db import connection




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

