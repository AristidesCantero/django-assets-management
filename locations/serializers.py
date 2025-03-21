from rest_framework import serializers
from locations.models import Business, Headquarters, InternalLocation


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'



class HeadquartersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headquarters
        fields = '__all__'

class InternalLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalLocation
        fields = '__all__'
    
