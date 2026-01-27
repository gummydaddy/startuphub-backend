from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import CoWorkingRoom, RoomMembership, RoomMessage, ProgressUpdate, ProgressReaction
from founders.serializers import FounderProfileSerializer
from django.db.models import Q

class CoWorkingRoomViewSet(viewsets.ModelViewSet):
    queryset = CoWorkingRoom.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # We'll define a simple serializer inline
        from rest_framework import serializers
        
        class CoWorkingRoomSerializer(serializers.ModelSerializer):
            member_count = serializers.IntegerField(read_only=True)
            is_member = serializers.SerializerMethodField()
            
            class Meta:
                model = CoWorkingRoom
                fields = ['id', 'name', 'emoji', 'description', 'is_active', 
                         'max_members', 'member_count', 'is_member', 'created_at']
                read_only_fields = ['id', 'created_at']
            
            def get_is_member(self, obj):
                request = self.context.get('request')
                if request and hasattr(request.user, 'founder_profile'):
                    return obj.members.filter(
                        founder=request.user.founder_profile,
                        is_active=True
                    ).exists()
                return False
        
        return CoWorkingRoomSerializer
    
    def list(self, request, *args, **kwargs):
        """List all active rooms with member counts"""
        queryset = self.get_queryset()
        
        # Add member count annotation
        from django.db.models import Count
        queryset = queryset.annotate(
            member_count=Count('members', filter=Q(members__is_active=True))
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a co-working room"""
        room = self.get_object()
        founder = request.user.founder_profile
        
        # Check if room is full
        active_members = room.members.filter(is_active=True).count()
        if active_members >= room.max_members:
            return Response(
                {'error': 'Room is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create membership
        membership, created = RoomMembership.objects.get_or_create(
            room=room,
            founder=founder,
            defaults={'is_active': True}
        )
        
        if not created:
            membership.is_active = True
            membership.save()
        
        return Response({
            'status': 'joined',
            'room_id': room.id,
            'room_name': room.name
        })
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a co-working room"""
        room = self.get_object()
        founder = request.user.founder_profile
        
        membership = RoomMembership.objects.filter(
            room=room,
            founder=founder
        ).first()
        
        if membership:
            membership.is_active = False
            membership.save()
        
        return Response({'status': 'left'})
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get active members in a room"""
        room = self.get_object()
        
        active_memberships = room.members.filter(is_active=True).select_related('founder')
        
        members_data = []
        for membership in active_memberships:
            members_data.append({
                'id': membership.founder.id,
                'name': membership.founder.name,
                'stage': membership.founder.stage,
                'industry': membership.founder.industry,
                'joined_at': membership.joined_at,
                'is_online': membership.founder.is_online
            })
        
        return Response(members_data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get recent messages in a room"""
        room = self.get_object()
        
        # Get last 50 messages
        messages = room.messages.all().select_related('sender')[:50]
        
        messages_data = [{
            'id': msg.id,
            'sender': {
                'id': msg.sender.id,
                'name': msg.sender.name
            },
            'content': msg.content,
            'created_at': msg.created_at
        } for msg in messages]
        
        return Response(messages_data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to a room (HTTP fallback, use WebSocket in production)"""
        room = self.get_object()
        founder = request.user.founder_profile
        content = request.data.get('content')
        
        if not content:
            return Response(
                {'error': 'Content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is member
        is_member = room.members.filter(
            founder=founder,
            is_active=True
        ).exists()
        
        if not is_member:
            return Response(
                {'error': 'Must join room first'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message = RoomMessage.objects.create(
            room=room,
            sender=founder,
            content=content
        )
        
        return Response({
            'id': message.id,
            'content': message.content,
            'created_at': message.created_at
        }, status=status.HTTP_201_CREATED)


class ProgressUpdateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class ProgressUpdateSerializer(serializers.ModelSerializer):
            founder_name = serializers.CharField(source='founder.name', read_only=True)
            reaction_count = serializers.SerializerMethodField()
            
            class Meta:
                model = ProgressUpdate
                fields = ['id', 'founder', 'founder_name', 'achievements', 
                         'failures', 'week_start', 'reaction_count', 'created_at']
                read_only_fields = ['id', 'founder', 'created_at']
            
            def get_reaction_count(self, obj):
                return obj.reactions.count()
        
        return ProgressUpdateSerializer
    
    def get_queryset(self):
        # Get all progress updates, or just user's own
        my_updates = self.request.query_params.get('my_updates', 'false')
        
        if my_updates.lower() == 'true':
            return ProgressUpdate.objects.filter(
                founder=self.request.user.founder_profile
            ).order_by('-created_at')
        
        return ProgressUpdate.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        """Automatically set founder to current user"""
        serializer.save(founder=self.request.user.founder_profile)
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add a reaction/comment to a progress update"""
        progress = self.get_object()
        comment = request.data.get('comment')
        
        if not comment:
            return Response(
                {'error': 'Comment is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reaction = ProgressReaction.objects.create(
            progress=progress,
            founder=request.user.founder_profile,
            comment=comment
        )
        
        return Response({
            'id': reaction.id,
            'comment': reaction.comment,
            'created_at': reaction.created_at
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def reactions(self, request, pk=None):
        """Get all reactions for a progress update"""
        progress = self.get_object()
        reactions = progress.reactions.all()
        
        reactions_data = [{
            'id': r.id,
            'founder': {
                'id': r.founder.id,
                'name': r.founder.name
            },
            'comment': r.comment,
            'created_at': r.created_at
        } for r in reactions]
        
        return Response(reactions_data)

