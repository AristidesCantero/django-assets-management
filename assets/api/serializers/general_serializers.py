from rest_framework import serializers
from assets.domain.models import Asset, SystemSegregation

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'


class SystemSegregationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSegregation
        fields = '__all__'