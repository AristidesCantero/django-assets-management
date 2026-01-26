from rest_framework import serializers
from locations.models import Headquarters, Business
from locations.serializers.serializers import validate_name, validate_phone



class HeadquartersUpdateSerializer(serializers.Serializer):

    class Meta:
        model = Headquarters
        fields = '__all__'
        extra_kwargs = {}


        name 
    address 
    phone 
    creation_date 


    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, required=True)
    address = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=15, required=True)
    business_key = serializers.IntegerField(required=True, validators=[validate_business_key])



    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.phone = validated_data.get('phone', instance.phone)
        updated_headquarter = instance
        instance.save()
        return updated_headquarter
    
    def validate_business_key(self, business_key):
        return validate_business_key(value=business_key)

   
        

class HeadquartersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headquarters
        fields = '__all__'

    name = serializers.CharField(max_length=100, required=True)
    address = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=15, required=True)
    business_key = serializers.IntegerField(required=True, validators=[validate_business_key])

    def validate_business_key(self, business_key):
        return validate_business_key(value=business_key)

    def to_representation(self, instance):
        # data = super().to_representation(instance) #this def representation is used to get the data is instance is a object
        business_key = instance['business_key']
        business = Business.objects.filter(id=business_key).values('name').first()
        return {
            instance['id']: {
            'id': instance['id'],
            'name': instance['name'],
            'address': instance['address'],
            'phone': instance['phone'],
            'business_key': instance['business_key'],
            'business_name': business['name'] if business else 'N/A'
            }
        }
    


def validate_business_key(value):
    if not Business.objects.filter(id=value.id).exists():
        raise serializers.ValidationError("Business does not exist.")
    return value
    

def validate_phone(value):
    if not value.isdigit() or len(value) < 10:
        raise serializers.ValidationError("Phone number must be numeric and at least 10 digits long.")
    return value
