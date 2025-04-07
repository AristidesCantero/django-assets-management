from locations.models import Headquarters, Business, InternalLocation
from locations.api.serializers import InternalLocationSerializer

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

#generic list view in case to be needed
class GeneralListAPIView(generics.ListAPIView):
    serializer_class = None

    def get_queryset(self):
        model = self.get_serializer().Meta.model
        return model.objects.all()

#this is used to get all the internallocations of the headquarters
class InternalLocationListAPIView(generics.ListAPIView):
    serializer_class = InternalLocationSerializer

    def get_queryset(self, pk=None):
        return InternalLocation.objects.filter(headquarters_key=pk)

class InternalLocationDetailAPIView(generics.CreateAPIView):
    serializer_class = InternalLocationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            #serializer.save()
            return Response({'message': 'Ubicación física creada exitosamente'}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    