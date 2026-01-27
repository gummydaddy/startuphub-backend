from django.contrib import admin
from .models import CoWorkingRoom, RoomMembership, RoomMessage, ProgressUpdate, ProgressReaction


@admin.register(CoWorkingRoom)
class CoWorkingRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'is_active', 'max_members', 'current_members', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def current_members(self, obj):
        return obj.members.filter(is_active=True).count()
    current_members.short_description = 'Active Members'


@admin.register(RoomMembership)
class RoomMembershipAdmin(admin.ModelAdmin):
    list_display = ['room', 'founder', 'is_active', 'joined_at', 'last_active']
    list_filter = ['is_active', 'joined_at']
    search_fields = ['room__name', 'founder__name']
    readonly_fields = ['joined_at', 'last_active']


@admin.register(RoomMessage)
class RoomMessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'content_short', 'created_at']
    list_filter = ['room', 'created_at']
    search_fields = ['content', 'sender__name', 'room__name']
    readonly_fields = ['created_at']
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Message'


@admin.register(ProgressUpdate)
class ProgressUpdateAdmin(admin.ModelAdmin):
    list_display = ['founder', 'week_start', 'achievements_count', 'failures_count', 'created_at']
    list_filter = ['week_start', 'created_at']
    search_fields = ['founder__name']
    readonly_fields = ['created_at']
    
    def achievements_count(self, obj):
        return len(obj.achievements)
    achievements_count.short_description = 'Achievements'
    
    def failures_count(self, obj):
        return len(obj.failures)
    failures_count.short_description = 'Failures'


@admin.register(ProgressReaction)
class ProgressReactionAdmin(admin.ModelAdmin):
    list_display = ['progress_short', 'founder', 'created_at']
    list_filter = ['created_at']
    search_fields = ['founder__name', 'comment']
    readonly_fields = ['created_at']
    
    def progress_short(self, obj):
        return f"{obj.progress.founder.name} - {obj.progress.week_start}"
    progress_short.short_description = 'Progress Update'

