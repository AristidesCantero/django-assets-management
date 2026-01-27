from rest_framework import serializers
from locations.models import Headquarters, Business




def validate_business_key(value):
    business = Business.objects.get(id=value)
    if not business:
        raise serializers.ValidationError("Business does not exist.")
    return business
    

def validate_phone(value):
    if not value.isdigit() or len(value) < 10:
        raise serializers.ValidationError("Phone number must be numeric and at least 10 digits long.")
    return value



class HeadquartersSerializer(serializers.Serializer):

    class Meta:
        model = Headquarters
        fields = '__all__'
        extra_kwargs = {}


    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, required=True)
    address = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=15, required=True)
    business_key = serializers.IntegerField(required=True, validators=[validate_business_key])


    def get(self, key):
        pass

    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.phone = validated_data.get('phone', instance.phone)
        updated_headquarter = instance
        instance.save()
        return updated_headquarter
    

class HeadquartersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headquarters
        fields = '__all__'

    name = serializers.CharField(max_length=100, required=True)
    address = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=15, required=True)
    business_key = serializers.IntegerField(required=True, validators=[validate_business_key])


    def create(self, validated_data):
        validated_data['business_key'] = Business.objects.get(id=validated_data['business_key'])
        headquarter = super().create(validated_data=validated_data)
        return headquarter

    def to_representation(self, instance):
        # data = super().to_representation(instance) #this def representation is used to get the data is instance is a object
        business_key = instance.business_key

        return {
            instance.id: {
            'id': instance.id,
            'name': instance.name,
            'address': instance.address,
            'phone': instance.phone,
            'business_key': instance.business_key.name,
            'business_name': business_key.name if business_key else 'N/A'
            }
        }
    


