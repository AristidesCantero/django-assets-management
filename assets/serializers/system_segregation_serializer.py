from rest_framework.serializers import *
from ..models import SystemSegregation


class SystemSegregationSerializer(ModelSerializer):
    class Meta:
        model = SystemSegregation
        fields = '__all__'