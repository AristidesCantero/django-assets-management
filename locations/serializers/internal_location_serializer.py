from rest_framework import serializers
from locations.models import InternalLocation, Headquarters




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

    def validate_headquarters_key(self, value):
            if not value:
                raise serializers.ValidationError("Headquarters key is required.")
            if not Headquarters.objects.filter(id=value).exists():
                raise serializers.ValidationError("Headquarters does not exist.")
            return value
            

class InternalLocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalLocation
        fields = '__all__'

    def to_representation(self, instance):
        # data = super().to_representation(instance) #this def representation is used to get the data is instance is a object
        headquarter_key = instance['headquarters_key']
        headquarter = Headquarters.objects.filter(id=headquarter_key).values('name').first()
        return {
            instance['id']: {
            'id': instance['id'],
            'name': instance['name'],
            'floor': instance['floor'],
            'room_number': instance['room_number'],
            'headquarters_key': instance['headquarters_key'],
            'headquarter_name': headquarter['name'] if headquarter else 'N/A'
            }
        }
    
