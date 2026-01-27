from django.contrib.auth.models import AbstractUser
from django.db import models

class CoWorkingRoom(models.Model):
    name = models.CharField(max_length=200)
    emoji = models.CharField(max_length=10)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    max_members = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.members.filter(is_active=True).count()


class RoomMembership(models.Model):
    room = models.ForeignKey(CoWorkingRoom, on_delete=models.CASCADE, related_name='members')
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['room', 'founder']


class RoomMessage(models.Model):
    room = models.ForeignKey(CoWorkingRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']


class ProgressUpdate(models.Model):
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE, related_name='progress_updates')
    achievements = models.JSONField(default=list)  # ["Launched landing page"]
    failures = models.JSONField(default=list)  # ["Failed Facebook ads"]
    week_start = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class ProgressReaction(models.Model):
    progress = models.ForeignKey(ProgressUpdate, on_delete=models.CASCADE, related_name='reactions')
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['progress', 'founder']
        ordering = ['created_at']
        
