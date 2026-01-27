from django.contrib.auth.models import AbstractUser
from django.db import models

class Idea(models.Model):
    author = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE, related_name='ideas')
    problem = models.TextField()
    solution = models.TextField()
    stage = models.CharField(max_length=100)
    need_help = models.TextField()
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.author.name} - {self.problem[:50]}"
    
    class Meta:
        ordering = ['-created_at']


class IdeaComment(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']


class IdeaUpvote(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='upvoters')
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['idea', 'founder']


class IdeaCollaboration(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='collaborators')
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
