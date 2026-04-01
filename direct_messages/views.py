# direct_messages/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import DirectMessage
from founders.models import FounderProfile


class DirectMessageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all messages for current user"""
        try:
            current_founder = request.user.founder_profile
            
            messages = DirectMessage.objects.filter(
                Q(from_founder=current_founder) | Q(to_founder=current_founder)
            ).select_related('from_founder', 'to_founder').order_by('-created_at')
            
            messages_data = [{
                'id': msg.id,
                'from_founder': msg.from_founder.id,
                'to_founder': msg.to_founder.id,
                'from_founder_details': {
                    'id': msg.from_founder.id,
                    'name': msg.from_founder.name,
                    'industry': msg.from_founder.industry,
                },
                'to_founder_details': {
                    'id': msg.to_founder.id,
                    'name': msg.to_founder.name,
                    'industry': msg.to_founder.industry,
                },
                'content': msg.content,
                'read': msg.read,
                'created_at': msg.created_at.isoformat(),
            } for msg in messages]
            
            return Response(messages_data)
        
        except AttributeError:
            return Response(
                {'error': 'Please create your founder profile first'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def create(self, request):
        """Send a direct message"""
        try:
            from_founder = request.user.founder_profile
            to_founder_id = request.data.get('to_founder')
            content = request.data.get('content')
            
            if not to_founder_id or not content:
                return Response(
                    {'error': 'to_founder and content are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            to_founder = FounderProfile.objects.get(id=to_founder_id)
            
            message = DirectMessage.objects.create(
                from_founder=from_founder,
                to_founder=to_founder,
                content=content.strip()
            )
            
            return Response({
                'id': message.id,
                'from_founder': from_founder.id,
                'to_founder': to_founder.id,
                'content': message.content,
                'read': message.read,
                'created_at': message.created_at.isoformat(),
            }, status=status.HTTP_201_CREATED)
        
        except FounderProfile.DoesNotExist:
            return Response(
                {'error': 'Founder not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except AttributeError:
            return Response(
                {'error': 'Please create your founder profile first'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='conversation/(?P<founder_id>[^/.]+)')
    def conversation(self, request, founder_id=None):
        """Get conversation with a specific founder"""
        try:
            current_founder = request.user.founder_profile
            other_founder = FounderProfile.objects.get(id=founder_id)
            
            messages = DirectMessage.objects.filter(
                (Q(from_founder=current_founder) & Q(to_founder=other_founder)) |
                (Q(from_founder=other_founder) & Q(to_founder=current_founder))
            ).order_by('created_at')
            
            # Mark messages as read
            DirectMessage.objects.filter(
                from_founder=other_founder,
                to_founder=current_founder,
                read=False
            ).update(read=True)
            
            messages_data = [{
                'id': msg.id,
                'from_founder': msg.from_founder.id,
                'to_founder': msg.to_founder.id,
                'content': msg.content,
                'read': msg.read,
                'created_at': msg.created_at.isoformat(),
            } for msg in messages]
            
            return Response(messages_data)
        
        except FounderProfile.DoesNotExist:
            return Response(
                {'error': 'Founder not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except AttributeError:
            return Response(
                {'error': 'Please create your founder profile first'},
                status=status.HTTP_400_BAD_REQUEST
            )
