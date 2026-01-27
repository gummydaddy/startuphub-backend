from rest_framework import serializers
from .models import FounderProfile, FounderConnection

class FounderProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = FounderProfile
        fields = [
            'id', 'email', 'name', 'country', 'timezone', 'stage',
            'industry', 'skills', 'looking_for', 'personality_tags',
            'current_goal', 'is_online', 'last_active', 'profile_image',
            'created_at'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'last_active']


class FounderProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FounderProfile
        fields = [
            'name', 'country', 'timezone', 'stage', 'industry',
            'skills', 'looking_for', 'personality_tags', 'current_goal'
        ]
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class FounderConnectionSerializer(serializers.ModelSerializer):
    from_founder_details = FounderProfileSerializer(source='from_founder', read_only=True)
    to_founder_details = FounderProfileSerializer(source='to_founder', read_only=True)
    
    class Meta:
        model = FounderConnection
        fields = ['id', 'from_founder', 'to_founder', 'from_founder_details', 
                  'to_founder_details', 'status', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
