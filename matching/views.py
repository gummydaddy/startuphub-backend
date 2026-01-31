from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from founders.models import FounderProfile
from founders.serializers import FounderProfileSerializer
import random


class MatchingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def roulette(self, request):
        """Find a random founder for video chat"""
        try:
            # Check if user has founder profile
            try:
                current_founder = request.user.founder_profile
            except AttributeError:
                return Response(
                    {'error': 'Please create your founder profile first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get all founders except current user
            all_founders = FounderProfile.objects.exclude(id=current_founder.id)
            
            if not all_founders.exists():
                return Response(
                    {'error': 'No other founders available right now. Invite your friends!'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Pick random founder
            matched_founder = random.choice(list(all_founders))
            
            serializer = FounderProfileSerializer(matched_founder)
            return Response({
                'session_id': random.randint(1000, 9999),
                'matched_founder': serializer.data
            })
        
        except Exception as e:
            return Response(
                {'error': f'Matching failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

