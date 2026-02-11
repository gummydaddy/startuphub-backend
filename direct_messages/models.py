# direct_messages/models.py

from django.db import models
from founders.models import FounderProfile


class DirectMessage(models.Model):
    from_founder = models.ForeignKey(
        FounderProfile, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    to_founder = models.ForeignKey(
        FounderProfile, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.from_founder.name} -> {self.to_founder.name}"
