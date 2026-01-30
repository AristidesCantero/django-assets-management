from rest_framework import serializers
from django.core.exceptions import ValidationError
from locations.models import InternalLocation, Headquarters, Business
from users.models import User


def validate_headquarters_key_ext(instance, context, model=None):
        if not instance:
            raise serializers.ValidationError("Headquarters key is required.")
        if not Headquarters.objects.filter(id=instance.id).exists():
            raise serializers.ValidationError("Headquarters does not exist.")
        
        user = context["request"].user
        request = context["request"]

        try:
            headquarter = Headquarters.objects.get(id=instance.id)
        except Headquarters.DoesNotExist:
             return []
             
        business = headquarter.get_business()

        allowed_business = User.objects.businesses_allowed_to_user(request=request,model=model)

        if not instance.id in allowed_business:
            raise ValidationError(f"User does not have permission over headquarters {headquarter.id} of business: {business.id}")
            
        business = Business.objects.get(id=instance.id)
        return  business


class InternalLocationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    headquarters_key = serializers.IntegerField(min_value=0)
    floor = serializers.CharField(max_length=10)
    room_number = serializers.CharField(max_length=10)
    class Meta:
            model = InternalLocation
            fields = '__all__'

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
         return validate_headquarters_key_ext(instance=instance, context=self.context, model = Headquarters).id
    

    def to_representation(self, instance):
        return {
           instance.id : {
                    instance.id,
                    instance.name,
                    instance.floor
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
        validated_data['headquarters_key'] = Headquarters.objects.get(id=validated_data['headquarters_key'])
        
        return super().create(validated_data=validated_data)
    

    def validate_headquarters_key(self, instance):
         return validate_headquarters_key_ext(instance=instance, context=self.context, model = Headquarters).id
    

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
    
