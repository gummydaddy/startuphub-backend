from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .services import MatchingService
from .models import RouletteSession, CofounderMatch
from founders.serializers import FounderProfileSerializer

class MatchingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def roulette(self, request):
        """Find a random founder for video chat"""
        try:
            current_founder = request.user.founder_profile
            matched_founder = MatchingService.find_roulette_match(current_founder)
            
            if not matched_founder:
                return Response(
                    {'error': 'No founders available right now'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create session
            session = RouletteSession.objects.create(
                founder=current_founder,
                matched_with=matched_founder
            )
            
            serializer = FounderProfileSerializer(matched_founder)
            return Response({
                'session_id': session.id,
                'matched_founder': serializer.data
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def cofounder_suggestions(self, request):
        """Get co-founder suggestions based on compatibility"""
        try:
            current_founder = request.user.founder_profile
            all_founders = FounderProfile.objects.exclude(id=current_founder.id)
            
            suggestions = []
            for founder in all_founders:
                score = MatchingService.calculate_compatibility(
                    current_founder, founder
                )
                suggestions.append({
                    'founder': FounderProfileSerializer(founder).data,
                    'compatibility_score': score
                })
            
            # Sort by compatibility
            suggestions.sort(key=lambda x: x['compatibility_score'], reverse=True)
            
            return Response(suggestions[:20])  # Top 20
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
