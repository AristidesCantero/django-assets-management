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

        def validate_business_key(self, value):
            if not Business.objects.filter(id=value).exists():
                raise serializers.ValidationError("Business does not exist.")
            return value
            
        
        def validate_phone(self, value):
            if not value.isdigit() or len(value) < 10:
                raise serializers.ValidationError("Phone number must be numeric and at least 10 digits long.")
            return value
        
        def create(self, validated_data):
            headquarter = Headquarters(**validated_data)
            print(headquarter)
            headquarter.save()
            return headquarter
    
        def update(self, instance, validated_data):
            updated_headquarter = super().update(instance, validated_data)
            updated_headquarter.save()
            return updated_headquarter



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
            print(headquarter)
            headquarter.save()
            return headquarter
    
        def update(self, instance, validated_data):
            updated_headquarter = instance.update(**validated_data)
            updated_headquarter.save()
            return updated_headquarter

        

class HeadquartersListSerializer(serializers.Serializer):
    class Meta:
        model = Headquarters
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        business_key = instance['business_key']
        business = Business.objects.filter(id=business_key).values('name').first()
        return {
            'id': instance['id'],
            'name': instance['name'],
            'address': instance['address'],
            'phone': instance['phone'],
            'business_key': instance['business_key'],
            'business_name': business['name'] if business else 'N/A'
        }

class InternalLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalLocation
        fields = '__all__'
    
