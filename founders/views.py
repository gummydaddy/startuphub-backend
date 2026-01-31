from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import FounderProfile, FounderConnection
from .serializers import FounderProfileSerializer


class FounderProfileViewSet(viewsets.ModelViewSet):
    queryset = FounderProfile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FounderProfileSerializer
    
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
    
    def create(self, request, *args, **kwargs):
        """Create founder profile - FIX: Automatically set user"""
        # Check if user already has a profile
        if hasattr(request.user, 'founder_profile'):
            return Response(
                {'error': 'You already have a founder profile'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get data from request
        data = request.data.copy()
        
        # Create profile with current user
        try:
            profile = FounderProfile.objects.create(
                user=request.user,
                name=data.get('name'),
                country=data.get('country'),
                timezone=data.get('timezone'),
                stage=data.get('stage'),
                industry=data.get('industry'),
                skills=data.get('skills', []),
                looking_for=data.get('looking_for'),
                personality_tags=data.get('personality_tags', []),
                current_goal=data.get('current_goal', '')
            )
            
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's founder profile"""
        try:
            profile = request.user.founder_profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except FounderProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found. Please complete your profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except FounderProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found. Please complete your profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['patch', 'put'])
    def update_profile(self, request):
        """Update current user's profile"""
        try:
            profile = request.user.founder_profile
            
            # Update fields
            for field in ['name', 'country', 'timezone', 'stage', 'industry', 
                         'skills', 'looking_for', 'personality_tags', 'current_goal']:
                if field in request.data:
                    setattr(profile, field, request.data[field])
            
            profile.save()
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        except FounderProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
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
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get connections for current user"""
        try:
            user_profile = self.request.user.founder_profile
            return FounderConnection.objects.filter(
                Q(from_founder=user_profile) | Q(to_founder=user_profile)
            ).select_related('from_founder', 'to_founder').order_by('-created_at')
        except AttributeError:
            return FounderConnection.objects.none()
    
    def list(self, request):
        """List all connections with founder details"""
        queryset = self.get_queryset()
        
        connections_data = []
        for conn in queryset:
            connections_data.append({
                'id': conn.id,
                'from_founder': conn.from_founder.id,
                'to_founder': conn.to_founder.id,
                'from_founder_details': {
                    'id': conn.from_founder.id,
                    'name': conn.from_founder.name,
                    'industry': conn.from_founder.industry,
                    'stage': conn.from_founder.stage,
                    'current_goal': conn.from_founder.current_goal,
                },
                'to_founder_details': {
                    'id': conn.to_founder.id,
                    'name': conn.to_founder.name,
                    'industry': conn.to_founder.industry,
                    'stage': conn.to_founder.stage,
                    'current_goal': conn.to_founder.current_goal,
                },
                'status': conn.status,
                'message': conn.message,
                'created_at': conn.created_at.isoformat(),
            })
        
        return Response(connections_data)
    
    def create(self, request):
        """Send connection request"""
        try:
            from_founder = request.user.founder_profile
            to_founder_id = request.data.get('to_founder')
            
            if not to_founder_id:
                return Response(
                    {'error': 'to_founder is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Don't allow self-connection
            try:
                to_founder_id_int = int(to_founder_id)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid to_founder ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if to_founder_id_int == from_founder.id:
                return Response(
                    {'error': 'Cannot connect with yourself'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                to_founder = FounderProfile.objects.get(id=to_founder_id)
            except FounderProfile.DoesNotExist:
                return Response(
                    {'error': 'Founder not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if connection already exists
            existing = FounderConnection.objects.filter(
                Q(from_founder=from_founder, to_founder=to_founder) |
                Q(from_founder=to_founder, to_founder=from_founder)
            ).first()
            
            if existing:
                return Response(
                    {'error': f'Connection already exists (status: {existing.status})'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create connection
            connection = FounderConnection.objects.create(
                from_founder=from_founder,
                to_founder=to_founder,
                message=request.data.get('message', ''),
                status='pending'
            )
            
            return Response({
                'id': connection.id,
                'status': 'pending',
                'message': 'Connection request sent successfully'
            }, status=status.HTTP_201_CREATED)
        
        except AttributeError:
            return Response(
                {'error': 'Please create your founder profile first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a connection request"""
        try:
            connection = self.get_object()
            current_user_profile = request.user.founder_profile
            
            # Only the receiver can accept
            if connection.to_founder != current_user_profile:
                return Response(
                    {'error': 'You can only accept requests sent to you'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            connection.status = 'accepted'
            connection.save()
            
            return Response({
                'status': 'accepted',
                'message': f'You are now connected with {connection.from_founder.name}'
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a connection request"""
        try:
            connection = self.get_object()
            current_user_profile = request.user.founder_profile
            
            # Only the receiver can reject
            if connection.to_founder != current_user_profile:
                return Response(
                    {'error': 'You can only reject requests sent to you'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            connection.status = 'rejected'
            connection.save()
            
            return Response({'status': 'rejected'})
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

