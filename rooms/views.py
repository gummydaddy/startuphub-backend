from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CoWorkingRoom, RoomMembership, RoomMessage


class CoWorkingRoomViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Allow viewing rooms and messages without strict auth"""
        if self.action in ['list', 'messages']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def list(self, request):
        """List all active rooms"""
        try:
            rooms = CoWorkingRoom.objects.filter(is_active=True)
            
            rooms_data = []
            for room in rooms:
                try:
                    member_count = RoomMembership.objects.filter(
                        room=room, 
                        is_active=True
                    ).count()
                except:
                    member_count = 0
                
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'emoji': room.emoji,
                    'description': room.description,
                    'is_active': room.is_active,
                    'max_members': room.max_members,
                    'member_count': member_count,
                })
            
            return Response(rooms_data)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages in a room"""
        try:
            room = CoWorkingRoom.objects.get(pk=pk)
            messages = RoomMessage.objects.filter(room=room).select_related('sender').order_by('-created_at')[:50]
            
            messages_data = [{
                'id': msg.id,
                'sender': {
                    'id': msg.sender.id,
                    'name': msg.sender.name
                },
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            } for msg in reversed(list(messages))]
            
            return Response(messages_data)
        except CoWorkingRoom.DoesNotExist:
            return Response(
                {'error': 'Room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to a room"""
        try:
            room = CoWorkingRoom.objects.get(pk=pk)
            
            # Check if user has founder profile
            try:
                founder = request.user.founder_profile
            except AttributeError:
                return Response(
                    {'error': 'Please create your founder profile first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            content = request.data.get('content')
            
            if not content or not content.strip():
                return Response(
                    {'error': 'Content is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            message = RoomMessage.objects.create(
                room=room,
                sender=founder,
                content=content.strip()
            )
            
            return Response({
                'id': message.id,
                'sender': {
                    'id': founder.id,
                    'name': founder.name
                },
                'content': message.content,
                'created_at': message.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)
        
        except CoWorkingRoom.DoesNotExist:
            return Response(
                {'error': 'Room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import traceback
            print(f"Error sending message: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'error': f'Failed to send message: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a co-working room"""
        try:
            room = CoWorkingRoom.objects.get(pk=pk)
            founder = request.user.founder_profile
            
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
        except CoWorkingRoom.DoesNotExist:
            return Response(
                {'error': 'Room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
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


class ProgressUpdateViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])
    
    def create(self, request):
        return Response({'status': 'created'}, status=status.HTTP_201_CREATED)
    

'''
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CoWorkingRoom, RoomMembership


class CoWorkingRoomViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all active rooms"""
        try:
            rooms = CoWorkingRoom.objects.filter(is_active=True)
            
            rooms_data = []
            for room in rooms:
                # Manually count members
                try:
                    member_count = RoomMembership.objects.filter(
                        room=room, 
                        is_active=True
                    ).count()
                except:
                    member_count = 0
                
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'emoji': room.emoji,
                    'description': room.description,
                    'is_active': room.is_active,
                    'max_members': room.max_members,
                    'member_count': member_count,
                })
            
            return Response(rooms_data)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a co-working room"""
        try:
            room = CoWorkingRoom.objects.get(pk=pk)
            founder = request.user.founder_profile
            
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
        except CoWorkingRoom.DoesNotExist:
            return Response(
                {'error': 'Room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a co-working room"""
        try:
            room = CoWorkingRoom.objects.get(pk=pk)
            founder = request.user.founder_profile
            
            membership = RoomMembership.objects.filter(
                room=room,
                founder=founder
            ).first()
            
            if membership:
                membership.is_active = False
                membership.save()
            
            return Response({'status': 'left'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProgressUpdateViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List progress updates"""
        return Response([])
    
    def create(self, request):
        """Create progress update"""
        return Response({'status': 'created'}, status=status.HTTP_201_CREATED)

'''