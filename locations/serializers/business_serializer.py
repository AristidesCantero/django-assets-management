from rest_framework import serializers
from locations.models import Business
from locations.serializers.serializers import validate_nit, validate_utr, validate_name




class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    

    def validate_tin(self, value):
        return validate_nit(value)
    
    def validate_utr(self, value):
        return validate_utr(value)

    def validate_name(self, value):
        return validate_name(value)
    

    def to_representation(self, instance):
        return {
            'id': instance['id'],
            'name': instance['name'],
            'tin': instance['tin'].upper(),
            'utr': instance['utr'].upper()
        }




class BusinessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'
        


    def get_queryset(self, pk=None):
        if pk is None:
            return Business.objects.all()
        return Business.objects.filter(id=pk).first()
    
    def create(self, validated_data):
        return super().create(validated_data)

    def validate_tin(self, value):
        return validate_nit(value)
    
    def validate_utr(self, value):
        return validate_utr(value)

    def validate_name(self, value):
        return validate_name(value)
        

    def to_representation(self, instance):
        # data = super().to_representation(instance) #this def representation is used to get the data is instance is a object
        return { 'id': instance.id, 'name': instance.name, 'tin': instance.tin, 'utr': instance.utr }