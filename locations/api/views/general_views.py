from locations.models import Headquarters, Business, InternalLocation
from locations.api.serializers import InternalLocationSerializer

from rest_framework import generics

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