from rest_framework import serializers
from locations.models import Business, Headquarters, InternalLocation
from users.models import User
import re


class HeadquartersCheckSerializer(serializers.Serializer):        
        id=serializers.IntegerField(read_only=True)
        business_key = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())
        # business = BusinessSerializer(read_only=True, source='business_key')
        name = serializers.CharField(max_length=100)
        address = serializers.CharField(max_length=255)
        phone = serializers.CharField(max_length=15)

        def validate_business_key(self, value):
            if not Business.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("Business does not exist.")
            return value
            
        
        def validate_phone(self, value):
            if not value.isdigit() or len(value) < 10:
                raise serializers.ValidationError("Phone number must be numeric and at least 10 digits long.")
            return value
        
        def create(self, validated_data):
            headquarter = Headquarters.objects.create(**validated_data)
            headquarter.save()
            return headquarter
    
        def update(self, instance, validated_data):
            updated_headquarter = instance.update(**validated_data)
            updated_headquarter.save()
            return updated_headquarter


def validate_nit(instance):
    nit_pattern = r'^[0-9]{9}-[0-9]$'  # Example pattern: 8 digits followed by a hyphen and a digit
    if not re.match(nit_pattern, instance):
        raise serializers.ValidationError("Invalid NIT format. Expected format: '123456780-9'")
    
    return instance


def validate_utr(instance):
    utr_pattern = r'^[a-zA-Z0-9]{10}$'  # Example pattern: 10 alphanumeric characters

    if not re.fullmatch(utr_pattern, instance):
        raise serializers.ValidationError("Invalid UTR format. Expected format: 10 alphanumeric characters.")
    
    return instance


def validate_name(instance):
    name_pattern = r'^[a-zA-Z.\- ]+$'
    if (not re.fullmatch(name_pattern, instance) or len(instance) > 255 or len(instance) < 3):
        raise serializers.ValidationError("Invalid name, the name can only have letters and '-' and the lenght should be more than 3 characters and less than 255")
    
    return instance