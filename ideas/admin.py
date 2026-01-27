from django.contrib import admin
from .models import Idea, IdeaComment, IdeaUpvote, IdeaCollaboration


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ['problem_short', 'author', 'stage', 'upvotes', 'created_at']
    list_filter = ['stage', 'created_at']
    search_fields = ['problem', 'solution', 'author__name']
    readonly_fields = ['upvotes', 'created_at', 'updated_at']
    
    def problem_short(self, obj):
        return obj.problem[:50] + '...' if len(obj.problem) > 50 else obj.problem
    problem_short.short_description = 'Problem'


@admin.register(IdeaComment)
class IdeaCommentAdmin(admin.ModelAdmin):
    list_display = ['idea_short', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__name', 'idea__problem']
    readonly_fields = ['created_at']
    
    def idea_short(self, obj):
        return obj.idea.problem[:30] + '...'
    idea_short.short_description = 'Idea'


@admin.register(IdeaUpvote)
class IdeaUpvoteAdmin(admin.ModelAdmin):
    list_display = ['idea_short', 'founder', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    
    def idea_short(self, obj):
        return obj.idea.problem[:30] + '...'
    idea_short.short_description = 'Idea'


@admin.register(IdeaCollaboration)
class IdeaCollaborationAdmin(admin.ModelAdmin):
    list_display = ['idea_short', 'founder', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['idea__problem', 'founder__name']
    readonly_fields = ['created_at']
    
    def idea_short(self, obj):
        return obj.idea.problem[:30] + '...'
    idea_short.short_description = 'Idea'
