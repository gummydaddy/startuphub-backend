# ideas/serializers.py
from rest_framework import serializers
from .models import Idea, IdeaComment, IdeaUpvote, IdeaCollaboration


class IdeaCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    
    class Meta:
        model = IdeaComment
        fields = ['id', 'idea', 'author', 'author_id', 'author_name', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class IdeaSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    comment_count = serializers.SerializerMethodField()
    user_upvoted = serializers.SerializerMethodField()
    comments = IdeaCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Idea
        fields = [
            'id', 'author', 'author_id', 'author_name', 'problem', 'solution',
            'stage', 'need_help', 'upvotes', 'comment_count',
            'user_upvoted', 'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'upvotes', 'created_at', 'updated_at']
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_user_upvoted(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'founder_profile'):
            return obj.upvoters.filter(founder=request.user.founder_profile).exists()
        return False


class IdeaCollaborationSerializer(serializers.ModelSerializer):
    founder_name = serializers.CharField(source='founder.name', read_only=True)
    idea_problem = serializers.CharField(source='idea.problem', read_only=True)
    
    class Meta:
        model = IdeaCollaboration
        fields = ['id', 'idea', 'idea_problem', 'founder', 'founder_name', 
                  'message', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']