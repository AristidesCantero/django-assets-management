from rest_framework import serializers
from components.domain.models import AssetSystem, SubsystemComponent, MinimumComponent

class AssetSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetSystem
        fields = '__all__'
    
class SubsystemComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubsystemComponent
        fields = '__all__'

class MinimumComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinimumComponent
        fields = '__all__'