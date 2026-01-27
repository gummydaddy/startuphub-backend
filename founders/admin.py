from django.contrib import admin
from .models import FounderProfile, FounderConnection


@admin.register(FounderProfile)
class FounderProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'stage', 'industry', 'looking_for', 'is_online', 'created_at']
    list_filter = ['stage', 'industry', 'looking_for', 'is_online']
    search_fields = ['name', 'user__email', 'industry', 'current_goal']
    readonly_fields = ['created_at', 'updated_at', 'last_active']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'name', 'country', 'timezone')
        }),
        ('Startup Info', {
            'fields': ('stage', 'industry', 'skills', 'current_goal')
        }),
        ('Preferences', {
            'fields': ('looking_for', 'personality_tags')
        }),
        ('Status', {
            'fields': ('is_online', 'last_active', 'profile_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FounderConnection)
class FounderConnectionAdmin(admin.ModelAdmin):
    list_display = ['from_founder', 'to_founder', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_founder__name', 'to_founder__name']
    readonly_fields = ['created_at', 'updated_at']
