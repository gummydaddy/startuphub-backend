from django.contrib.auth.models import AbstractUser
from django.db import models

class FounderProfile(models.Model):
    STAGE_CHOICES = [
        ('idea', 'Idea'),
        ('mvp', 'MVP'),
        ('launched', 'Launched'),
        ('scaling', 'Scaling'),
    ]
    
    LOOKING_FOR_CHOICES = [
        ('cofounder', 'Co-founder'),
        ('feedback', 'Feedback'),
        ('users', 'Users'),
        ('networking', 'Just networking'),
    ]
    
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='founder_profile')
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    industry = models.CharField(max_length=100)
    skills = models.JSONField(default=list)  # ["Tech", "Marketing"]
    looking_for = models.CharField(max_length=20, choices=LOOKING_FOR_CHOICES)
    personality_tags = models.JSONField(default=list)  # ["🚀 Fast executor"]
    current_goal = models.TextField()
    is_online = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.stage}"
    
    class Meta:
        ordering = ['-created_at']


class FounderConnection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    from_founder = models.ForeignKey(FounderProfile, on_delete=models.CASCADE, related_name='sent_connections')
    to_founder = models.ForeignKey(FounderProfile, on_delete=models.CASCADE, related_name='received_connections')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['from_founder', 'to_founder']
        ordering = ['-created_at']
