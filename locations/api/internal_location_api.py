from rest_framework import status
from rest_framework.generics import *
from rest_framework.response import Response
from permissions.permissions import permissionToCheckModel
from rest_framework_simplejwt.authentication import JWTAuthentication
from locations.serializers.internal_location_serializer import InternalLocationSerializer, InternalLocationListSerializer
from locations.querysets import InternalLocationQuerySet
from locations.models import InternalLocation





class InternalLocationAPIView(ListCreateAPIView):
    serializer_class = InternalLocationSerializer
    permission_classes = [permissionToCheckModel]
    authentication_classes = [JWTAuthentication]
    allowed_methods = ["GET", "PATCH", "DELETE"]

    def get_queryset(self,request, pk=None):
        internal_location =  InternalLocationQuerySet().internal_location_if_user_has_perm(request=request, pk=pk)
        if not internal_location["exists"]:
            raise InternalLocation.DoesNotExist
        return internal_location['hq']

    def get(self, request, pk=None):
        try:
            internal_location = self.get_queryset(request=request, pk=pk)
            response_data = {
                "data": self.serializer_class(internal_location)
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except InternalLocation.DoesNotExist:
            return Response({'detail': 'Headquarter has not been found.'}, status=status.HTTP_404_NOT_FOUND)

        
    

    def post(self, request):
        serializer = self.serializer_class(data = request.data, context={"request":request})

        response_data = {}
        if serializer.is_valid():
            serializer.save()
            response_data['data'] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data = {
            'errors': serializer.errors,
            'message': 'Error al crear la ubicación interna'
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    


class InternalLocationListAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = InternalLocationListSerializer
    permission_classes = [permissionToCheckModel]
    authentication_classes = [JWTAuthentication]
    allowed_methods = ["GET", "POST"]


    def get_queryset(self, request):
        internal_locations = InternalLocationQuerySet().get_user_internal_locations(request=request)
        return internal_locations

    def get(self, request):
        dictionary = self.get_queryset(request=request)
        new_internal_locations = {}
        if dictionary.keys():
            for business in dictionary.keys():
                new_internal_locations[business] = {}
                for headquarter in dictionary[business].keys():
                    internal_locations = dictionary[business][headquarter]
                    new_instance = self.serializer_class(internal_locations, many=True).data
                    new_internal_locations[business][headquarter] = new_instance if internal_locations else []


        context = {
            "data" : new_internal_locations
        }
        return Response(context, status=status.HTTP_200_OK)
    

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request":request})
        response_data = {}
        if serializer.is_valid():
            serializer.save()
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)