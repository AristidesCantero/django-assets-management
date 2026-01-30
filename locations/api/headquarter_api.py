from rest_framework.generics import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from locations.serializers.headquarter_serializer import HeadquartersListSerializer, HeadquartersSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from permissions.permissions import permissionToCheckModel
from locations.querysets import HeadquartersQuerySet
from locations.models import Headquarters


class HeadquarterAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = HeadquartersSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionToCheckModel]
    allowed_methods = ["GET", "POST"]


    def get_queryset(self, request, pk):
        headquarter =  HeadquartersQuerySet().headquarter_user_has_permission(request=request, pk=pk)
        if not headquarter["exists"]:
            raise Headquarters.DoesNotExist
        return headquarter['hq']


    def get(self, request, pk):
        try:
            headquarter = self.get_queryset(request=request, pk=pk)

            response_data = {
                "data": self.serializer_class(headquarter).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Headquarters.DoesNotExist:
            return Response({'detail': 'Headquarter has not been found.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    def delete(self, request):
        pass




class HeadquarterListAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = HeadquartersListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionToCheckModel]
    allowed_methods = ["GET", "POST"]


    def get_queryset(self, request):
        user_headquarters = HeadquartersQuerySet().get_user_headquarters(request=request)
        return user_headquarters

    def get(self, request):
        headquarters = self.get_queryset(request=request)
        new_headquarters = {}
        for business in headquarters.keys():
            new_headquarters[business] = self.serializer_class(headquarters[business], many=True).data
        

        context = {
            'data':new_headquarters
        }
        return Response(context, status=status.HTTP_200_OK)
        
        

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        response_data = {}
        if serializer.is_valid():
            serializer.save()
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)