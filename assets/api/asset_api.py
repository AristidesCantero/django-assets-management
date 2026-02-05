from assets.models import *
from assets.serializers.general_serializers import *
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from permissions.permissions import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
#las vistas definen el comportamiento de la API

##estas lineas permiten omitir la autenticacion y permisos para defs
#@authentication_classes([])
#@permission_classes([])

class AssetListAPIView(ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionToCheckModel]
    serializer_class = AssetSerializer
    allowed_methods = ['GET', 'POST']   

    def get_queryset(self):
        return Asset.objects.all()
    
    def get(self, request, *args, **kwargs):
        assets = self.get_queryset()
        serializer = self.serializer_class(assets, many=True)
        response_data = {}
        response_data['data'] = serializer.data

        if not assets:
            return Response({'detail': 'No assets found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(response_data, status=status.HTTP_200_OK)

    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    

class AssetAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissionToCheckModel] 
    serializer_class = AssetSerializer
    allowed_methods = ['GET', 'PATCH', 'DELETE']

    def get_queryset(self, user=None, pk=None):
        if not user or not pk:
            return []
        return Asset.objects.get(pk=pk)

    def get(self, request, pk, *args, **kwargs):
        try:
            asset = self.get_object()
            serializer = self.serializer_class(asset)
            response_data = {}
            response_data['data'] = serializer.data
            return Response(response_data, status=status.HTTP_200_OK)
        except Asset.DoesNotExist:
            return Response({'detail': 'Asset has not been found.'}, status=status.HTTP_404_NOT_FOUND)


    def patch(self, request, pk, *args, **kwargs):
        try:
            asset = self.get_object()
        except Asset.DoesNotExist:
            return Response({'detail': 'Asset has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(asset, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, pk, *args, **kwargs):
        try:
            asset = self.get_object()
            asset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Asset.DoesNotExist:
            return Response({'detail': 'Asset has not been found.'}, status=status.HTTP_404_NOT_FOUND)
        
