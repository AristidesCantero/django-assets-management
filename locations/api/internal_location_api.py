from rest_framework import status
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from locations.serializers.internal_location_serializer import InternalLocationSerializer, InternalLocationListSerializer





class InternalLocationAPI(ListCreateAPIView):
    serializer_class = InternalLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, pk=None):
        return self.serializer_class.Meta.model.objects.filter(headquarters_key=pk)

    def get(self, request, pk=None):
        internal_locations = self.get_queryset(pk=pk)
        response_data = {}
        if internal_locations.exists():
            serializer = self.serializer_class(internal_locations, many=True)
            response_data['data'] = serializer.data
            return Response(response_data, status=status.HTTP_200_OK)
        response_data['errors'] = 'No se han encontrado ubicaciones internas'
        response_data['message'] = 'No existen ubicaciones internas para la sede proporcionada'
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    

    def post(self, request):
        serializer = self.serializer_class(data = request.data)

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
    

