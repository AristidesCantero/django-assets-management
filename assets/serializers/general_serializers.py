from rest_framework.serializers import ModelSerializer
from ..models import Asset




class AssetSerializer(ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

    
    def to_representation(self, instance):
        return {
                    'id': instance.id,
                    'name': instance.name,
                    'description': instance.description,
                    'asset_tag': instance.asset_tag,
                    'serial_number': instance.serial_number,
                    'purchase_date': instance.purchase_date,
                    'warranty_expiration': instance.warranty_expiration,
                    'value': instance.value,
                    'location': instance.location,
                    'assigned_to': instance.assigned_to.id if instance.assigned_to else None,
                    'status': instance.status,
                    'system_segregation': instance.system_segregation.id if instance.system_segregation else None,
                }
