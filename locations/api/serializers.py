from rest_framework import serializers
from locations.models import Business, Headquarters, InternalLocation
from locations.models import UserBusinessMember
from users.models import User
import re



class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

class BusinessCheckSerializer(serializers.Serializer):
    class Meta:
        model = Business
        fields = '__all__'


    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    tin = serializers.CharField(max_length=255)
    utr = serializers.CharField(max_length=255)
    


    def validate_name(self, value):
        pattern = r'^[a-zA-Z0-9.\- ]+$'
        if (not re.fullmatch(pattern, value) or len(value) > 255 or len(value) < 3):
            raise serializers.ValidationError("Invalid name, the name can only have numbers, letters and '-' and the lenght should be more than 3 characters and less than 255")
        return value
        
    def create(self, validated_data):
        business = Business.objects.create(**validated_data)
        business.save()
        return business
    
    def update(self, instance, validated_data):
        updated_business = instance.update(**validated_data)
        updated_business.save()
        return updated_business


class BusinessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

    def to_representation(self, instance):
        # data = super().to_representation(instance) #this def representation is used to get the data is instance is a object
        return {
            instance['id']: {
            'id': instance['id'],
            'name': instance['name'],
            'tin': instance['tin'],
            'utr': instance['utr']
        }
        }


class UserBusinessMemberSerializer(serializers.Serializer):
    class Meta:
        model = UserBusinessMember
        fields = '__all__'

    id = serializers.IntegerField(read_only=True)
    user_key = serializers.IntegerField(min_value=0)
    business_key = serializers.IntegerField(min_value=0)

    def validate_user_key(self, value):
        if not value:
            raise serializers.ValidationError("User key is required.")
        from users.models import User
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist.")
        return value

    def validate_business_key(self, value):
        if not value:
            raise serializers.ValidationError("Business key is required.")
        if not Business.objects.filter(id=value).exists():
            raise serializers.ValidationError("Business does not exist.")
        return value

class UserBusinessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBusinessMember
        fields = '__all__'

    def to_representation(self, instance):
        # data = super().to_representation(instance) #this def representation is used to get the data is instance is a object
        user_key = instance['user_key']
        business_key = instance['business_key']
        user = User.objects.filter(id=user_key).values('email').first()
        business = Business.objects.filter(id=business_key).values('name').first()
        return {
            instance['id']: {
            'id': instance['id'],
            'user_key': instance['user_key'],
            'user_email': user['email'] if user else 'N/A',
            'business_key': instance['business_key'],
            'business_name': business['name'] if business else 'N/A'
            }
        }

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


class HeadquartersUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
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
            
   
class InternalLocationCheckSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    headquarters_key = serializers.PrimaryKeyRelatedField(queryset=Headquarters.objects.all())
    floor = serializers.CharField(max_length=10)
    room_number = serializers.CharField(max_length=10)

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name is required.")
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value
    
    def validate_floor(self, value):
        if not value:
            raise serializers.ValidationError("Floor is required.")
        if len(value) < 3:
            raise serializers.ValidationError("Floor must be at least 3 character long.")
        return value
    
    def validate_room_number(self, value):
        if not value:
            raise serializers.ValidationError("Room number is required.")
        if len(value) < 3:
            raise serializers.ValidationError("Room number must be at least 3 character long.")
        return value

    def validate_headquarters_key(self, value):
            if not value:
                raise serializers.ValidationError("Headquarters key is required.")
            if not Headquarters.objects.filter(id=value.id).exists():
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
    
class InternalLocationUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    headquarters_key = serializers.PrimaryKeyRelatedField(queryset=Headquarters.objects.all())
    floor = serializers.CharField(max_length=10)
    room_number = serializers.CharField(max_length=10)

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name is required.")
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value
    
    def validate_floor(self, value):
        if not value:
            raise serializers.ValidationError("Floor is required.")
        if len(value) < 3:
            raise serializers.ValidationError("Floor must be at least 3 character long.")
        return value
    
    def validate_room_number(self, value):
        if not value:
            raise serializers.ValidationError("Room number is required.")
        if len(value) < 3:
            raise serializers.ValidationError("Room number must be at least 3 character long.")
        return value

    def validate_headquarters_key(self, value):
            if not value:
                raise serializers.ValidationError("Headquarters key is required.")
            if not Headquarters.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("Headquarters does not exist.")
            return value
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.floor = validated_data.get('floor', instance.floor)
        instance.room_number = validated_data.get('room_number', instance.room_number)
        return super().update(instance, validated_data)