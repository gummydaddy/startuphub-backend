from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CoWorkingRoom, RoomMembership, RoomMessage


class CoWorkingRoomViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all active rooms with accurate member counts"""
        try:
            rooms = CoWorkingRoom.objects.filter(is_active=True)
            
            rooms_data = []
            for room in rooms:
                # Count ACTIVE members in the room
                member_count = RoomMembership.objects.filter(
                    room=room,
                    is_active=True
                ).count()
                
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'emoji': room.emoji,
                    'description': room.description,
                    'is_active': room.is_active,
                    'max_members': room.max_members,
                    'member_count': member_count,  # This is now accurate
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
            
            try:
                founder = request.user.founder_profile
            except AttributeError:
                return Response(
                    {'error': 'Please create your founder profile first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create or activate membership
            membership, created = RoomMembership.objects.get_or_create(
                room=room,
                founder=founder,
                defaults={'is_active': True}
            )
            
            if not created and not membership.is_active:
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
            } for msg in reversed(list(messages))]  # Reverse to show oldest first
            
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
        """Send a message to a room - WITH DETAILED ERROR LOGGING"""
        import traceback
        
        try:
            print(f"\n=== SEND MESSAGE DEBUG ===")
            print(f"Room ID: {pk}")
            print(f"User: {request.user}")
            print(f"Request data: {request.data}")
            
            room = CoWorkingRoom.objects.get(pk=pk)
            print(f"Room found: {room.name}")
            
            # Check if user has founder profile
            try:
                founder = request.user.founder_profile
                print(f"Founder: {founder.name}")
            except AttributeError as e:
                print(f"No founder profile: {e}")
                return Response(
                    {'error': 'Please create your founder profile first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            content = request.data.get('content')
            print(f"Content: {content}")
            
            if not content or not content.strip():
                print("Content is empty!")
                return Response(
                    {'error': 'Message content is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create message
            print("Creating message...")
            message = RoomMessage.objects.create(
                room=room,
                sender=founder,
                content=content.strip()
            )
            print(f"Message created with ID: {message.id}")
            
            response_data = {
                'id': message.id,
                'sender': {
                    'id': founder.id,
                    'name': founder.name
                },
                'content': message.content,
                'created_at': message.created_at.isoformat()
            }
            print(f"Returning response: {response_data}")
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except CoWorkingRoom.DoesNotExist:
            print(f"Room {pk} not found!")
            return Response(
                {'error': 'Room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"ERROR: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Failed to send message: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProgressUpdateViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])