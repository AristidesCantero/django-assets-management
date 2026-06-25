from rest_framework import serializers
from users.domain.models import Invitation
from users.presentation.serializers.token_generator import send_invitation_email
from users.domain.models import User
from permissions.domain.models import Business



class UserInvitationSerializer(serializers.Serializer):
    class Meta:
        model = Invitation
        
  
    business = serializers.IntegerField(required=True)
    receiver = serializers.IntegerField(required=True)
    
    
    def validate_business(self, value):
      business = Business.objects.filter(id=value).first()
      if not business:
        raise serializers.ValidationError("Business doesnt exist")
      print(business)
      return business
    
    def validate_receiver(self, value):
      user = User.objects.filter(id=value).first()
      if not user:
        raise serializers.ValidationError("User doesnt exist")
      return user


    def validate(self, data):
        receiver = data["receiver"]
        business = data["business"]
        
        invitation = Invitation.objects.filter(user=receiver.id, business=business).first()
        if invitation.is_accepted:
          raise serializers.ValidationError("User already invited and accepted in business")
        
        data['invitation'] = invitation
        
        return data
        

    def create(self, validated_data):
        sender = self.context.get('sender')
        receiver = validated_data["receiver"]
        business = validated_data["business"]
        invitation = validated_data['invitation'] 
        
        
        resent = False
        if invitation:
          raw_token = Invitation.refresh_old_token(user=receiver)
          resent=True
        else:
          raw_token = Invitation.generate_token(user=receiver,business=business)
          
        email_sent = send_invitation_email(receiver,raw_token,business,sender)
        
        return receiver, resent