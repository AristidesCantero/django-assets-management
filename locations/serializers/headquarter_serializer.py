from rest_framework import serializers
from locations.models import Headquarters, Business
from django.core.exceptions import ValidationError
from users.models import User



def validate_business_key_ext(instance, context, model=None):
        user = context["request"].user
        request = context["request"]

        if not Business.objects.filter(pk=instance).exists():
            raise ValidationError("Business does not exist")

        allowed_business = User.objects.businesses_allowed_to_user(request=request,model=model)

        if not str(instance) in allowed_business:
            raise ValidationError("User does not have permission over business: "+str(instance))
            
        business = Business.objects.get(id=instance)
        return  business
    

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
    business_key = serializers.IntegerField(required=True)

    def validate_business_key(self, instance):
        return validate_business_key_ext(instance=instance, context=self.context, model = Headquarters).id



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
    business_key = serializers.IntegerField(required=True)

    def validate_business_key(self, instance):
        return validate_business_key_ext(instance=instance, context=self.context, model = Headquarters).id

    def create(self, validated_data):
        validated_data['business_key'] = Business.objects.get(id=validated_data['business_key'])
        return super().create(validated_data=validated_data)

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


    





        
    


