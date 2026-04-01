from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Idea, IdeaComment, IdeaUpvote, IdeaCollaboration
from .serializers import IdeaSerializer, IdeaCommentSerializer


class IdeaViewSet(viewsets.ModelViewSet):
    queryset = Idea.objects.all()
    serializer_class = IdeaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Idea.objects.all()
        
        # Filter by stage
        stage = self.request.query_params.get('stage')
        if stage:
            queryset = queryset.filter(stage__icontains=stage)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Automatically set the author to current user's founder profile"""
        try:
            serializer.save(author=self.request.user.founder_profile)
        except Exception as e:
            raise Exception(f"Error creating idea: {str(e)}")
    
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        """Upvote an idea"""
        try:
            idea = self.get_object()
            founder = request.user.founder_profile
            
            # Check if already upvoted
            upvote, created = IdeaUpvote.objects.get_or_create(
                idea=idea,
                founder=founder
            )
            
            if created:
                # New upvote
                idea.upvotes += 1
                idea.save()
                return Response({
                    'status': 'upvoted',
                    'upvotes': idea.upvotes
                })
            else:
                # Remove upvote
                upvote.delete()
                idea.upvotes = max(0, idea.upvotes - 1)
                idea.save()
                return Response({
                    'status': 'removed',
                    'upvotes': idea.upvotes
                })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        """Add a comment to an idea"""
        try:
            idea = self.get_object()
            content = request.data.get('content')
            
            if not content:
                return Response(
                    {'error': 'Content is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            comment = IdeaComment.objects.create(
                idea=idea,
                author=request.user.founder_profile,
                content=content
            )
            
            serializer = IdeaCommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all comments for an idea"""
        try:
            idea = self.get_object()
            comments = idea.comments.all()
            serializer = IdeaCommentSerializer(comments, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def collaborate(self, request, pk=None):
        """Request to collaborate on an idea"""
        try:
            idea = self.get_object()
            founder = request.user.founder_profile
            message = request.data.get('message', '')
            
            # Don't allow self-collaboration
            if idea.author == founder:
                return Response(
                    {'error': 'Cannot collaborate on your own idea'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if already requested
            existing = IdeaCollaboration.objects.filter(
                idea=idea,
                founder=founder
            ).first()
            
            if existing:
                return Response(
                    {'error': 'Collaboration request already sent'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            collaboration = IdeaCollaboration.objects.create(
                idea=idea,
                founder=founder,
                message=message
            )
            
            return Response({
                'status': 'collaboration_requested',
                'id': collaboration.id
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

'''
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Idea, IdeaComment, IdeaUpvote, IdeaCollaboration
from .serializers import IdeaSerializer, IdeaCommentSerializer


class IdeaViewSet(viewsets.ModelViewSet):
    queryset = Idea.objects.all()
    serializer_class = IdeaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Idea.objects.all()
        
        # Filter by stage
        stage = self.request.query_params.get('stage')
        if stage:
            queryset = queryset.filter(stage__icontains=stage)
        
        # Filter by industry (from author's profile)
        industry = self.request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(author__industry=industry)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Automatically set the author to current user's founder profile"""
        serializer.save(author=self.request.user.founder_profile)
    
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        """Upvote an idea"""
        idea = self.get_object()
        founder = request.user.founder_profile
        
        # Check if already upvoted
        upvote, created = IdeaUpvote.objects.get_or_create(
            idea=idea,
            founder=founder
        )
        
        if created:
            idea.upvotes += 1
            idea.save()
            return Response({'status': 'upvoted', 'upvotes': idea.upvotes})
        else:
            # Remove upvote
            upvote.delete()
            idea.upvotes = max(0, idea.upvotes - 1)
            idea.save()
            return Response({'status': 'removed', 'upvotes': idea.upvotes})
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        """Add a comment to an idea"""
        idea = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response(
                {'error': 'Content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comment = IdeaComment.objects.create(
            idea=idea,
            author=request.user.founder_profile,
            content=content
        )
        
        serializer = IdeaCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all comments for an idea"""
        idea = self.get_object()
        comments = idea.comments.all()
        serializer = IdeaCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def collaborate(self, request, pk=None):
        """Request to collaborate on an idea"""
        idea = self.get_object()
        founder = request.user.founder_profile
        message = request.data.get('message', '')
        
        # Don't allow self-collaboration
        if idea.author == founder:
            return Response(
                {'error': 'Cannot collaborate on your own idea'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already requested
        existing = IdeaCollaboration.objects.filter(
            idea=idea,
            founder=founder
        ).first()
        
        if existing:
            return Response(
                {'error': 'Collaboration request already sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        collaboration = IdeaCollaboration.objects.create(
            idea=idea,
            founder=founder,
            message=message
        )
        
        return Response({
            'status': 'collaboration_requested',
            'id': collaboration.id
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def collaborators(self, request, pk=None):
        """Get collaboration requests for an idea"""
        idea = self.get_object()
        
        # Only idea author can see collaboration requests
        if idea.author.user != request.user:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        collaborations = idea.collaborators.all()
        data = [{
            'id': c.id,
            'founder': {
                'id': c.founder.id,
                'name': c.founder.name,
                'skills': c.founder.skills,
                'industry': c.founder.industry
            },
            'message': c.message,
            'status': c.status,
            'created_at': c.created_at
        } for c in collaborations]
        
        return Response(data)
'''
