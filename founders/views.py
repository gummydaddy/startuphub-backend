from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FounderProfile, FounderConnection
from .serializers import FounderProfileSerializer, FounderProfileCreateSerializer, FounderConnectionSerializer

class FounderProfileViewSet(viewsets.ModelViewSet):
    queryset = FounderProfile.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FounderProfileCreateSerializer
        return FounderProfileSerializer
    
    def get_queryset(self):
        queryset = FounderProfile.objects.all()
        
        # Filters for co-founder matching
        stage = self.request.query_params.get('stage')
        industry = self.request.query_params.get('industry')
        looking_for = self.request.query_params.get('looking_for')
        
        if stage and stage != 'all':
            queryset = queryset.filter(stage=stage)
        if industry and industry != 'all':
            queryset = queryset.filter(industry=industry)
        if looking_for and looking_for != 'all':
            queryset = queryset.filter(looking_for=looking_for)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's founder profile"""
        try:
            profile = request.user.founder_profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except FounderProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['patch'])
    def update_online_status(self, request):
        """Update founder's online status"""
        try:
            profile = request.user.founder_profile
            profile.is_online = request.data.get('is_online', False)
            profile.save()
            return Response({'status': 'updated'})
        except FounderProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = FounderConnection.objects.all()
    serializer_class = FounderConnectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_profile = self.request.user.founder_profile
        return FounderConnection.objects.filter(
            models.Q(from_founder=user_profile) | models.Q(to_founder=user_profile)
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a connection request"""
        connection = self.get_object()
        if connection.to_founder.user != request.user:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        connection.status = 'accepted'
        connection.save()
        return Response({'status': 'accepted'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a connection request"""
        connection = self.get_object()
        if connection.to_founder.user != request.user:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        connection.status = 'rejected'
        connection.save()
        return Response({'status': 'rejected'})
