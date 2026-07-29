from rest_framework import serializers
from django.core.exceptions import ValidationError
from locations.models import InternalLocation, Headquarters, Business
from users.models import User


def validate_headquarters_key_ext(instance, context, model=None)-> str:
        if not instance:
            raise serializers.ValidationError("Headquarters key is required.")
        if not Headquarters.objects.filter(pk=instance).first():
            raise serializers.ValidationError("Headquarters does not exist.")
        
        user = context["request"].user
        request = context["request"]

        headquarter = []
        try:
            headquarter = Headquarters.objects.get(id=instance)
        except Headquarters.DoesNotExist:
             raise ValidationError(f'Headquarter with id {instance} does not exists')
             
        business = headquarter.get_business()

        allowed_business = User.objects.businesses_allowed_to_user(request=request,model=model)
        allowed_business = list(map(str,allowed_business))
        
        if not str(business.id) in allowed_business:
            raise ValidationError(f"User does not have permission over headquarters {headquarter.id} of business: {business.id}")

            
        return headquarter


class InternalLocationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    headquarters_key = serializers.IntegerField(min_value=0,validators=[])
    floor = serializers.CharField(max_length=10,validators=[])
    room_number = serializers.CharField(max_length=10,validators=[])
    class Meta:
            model = InternalLocation
            fields = '__all__'


    def update(self, instance, validated_data):
        instance.name = validated_data.get('name',instance.name)
        instance.floor = validated_data.get('floor',instance.floor)
        instance.room_number = validated_data.get('room_number',instance.room_number)
        updated_internal_location = instance
        instance.save()
        return updated_internal_location
    

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name is required.")
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value
    
    def validate_floor(self, value):
        if not value:
            raise serializers.ValidationError("Floor is required.")
        if len(value) < 1:
            raise serializers.ValidationError("Floor must be at least 1 character long.")
        return value
    
    def validate_room_number(self, value):
        if not value:
            raise serializers.ValidationError("Room number is required.")
        if len(value) < 1:
            raise serializers.ValidationError("Room number must be at least 1 character long.")
        return value


    def validate_headquarters_key(self, instance):
        validated_hq_key = validate_headquarters_key_ext(instance=instance.id, context=self.context, model = InternalLocation)
        return validated_hq_key

    def to_representation(self, instance):
        return {
           instance.id : {
                    "name":instance.name,
                    "floor":instance.floor,
                    'room_number': instance.room_number,
                    'headquarters': instance.headquarters_key.name if instance.headquarters_key else 'N/A',

            }
        }
            

class InternalLocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalLocation
        fields = '__all__'

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True)
    headquarters_key = serializers.PrimaryKeyRelatedField(queryset=Headquarters.objects.all(),required=True)
    floor = serializers.CharField(max_length=10,required=True)
    room_number = serializers.CharField(max_length=10,required=True)

    def create(self, validated_data):
        return super().create(validated_data=validated_data)
    

    def validate_headquarters_key(self, instance):
        validated_hq_key = validate_headquarters_key_ext(instance=instance.id, context=self.context, model = InternalLocation)
        return validated_hq_key
    

    def to_representation(self, instance):
        # data = super().to_representation(instance) #this def representation is used to get the data is instance is a object
        headquarter = instance.headquarters_key
        return {
            instance.id: {
            'id': instance.id,
            'name': instance.name,
            'floor': instance.floor,
            'room_number': instance.room_number,
            'headquarters_key': instance.headquarters_key.id,
            'headquarter_name': headquarter.name if headquarter else 'N/A'
            }
        }
    
