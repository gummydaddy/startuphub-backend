from django.contrib import admin
from .models import RouletteSession, CofounderMatch


@admin.register(RouletteSession)
class RouletteSessionAdmin(admin.ModelAdmin):
    list_display = ['founder', 'matched_with', 'connected', 'duration_seconds', 'started_at']
    list_filter = ['connected', 'started_at']
    search_fields = ['founder__name', 'matched_with__name']
    readonly_fields = ['started_at']


@admin.register(CofounderMatch)
class CofounderMatchAdmin(admin.ModelAdmin):
    list_display = ['founder1', 'founder2', 'compatibility_score', 'interested_founder1', 'interested_founder2', 'created_at']
    list_filter = ['interested_founder1', 'interested_founder2', 'created_at']
    search_fields = ['founder1__name', 'founder2__name']
    readonly_fields = ['created_at']
