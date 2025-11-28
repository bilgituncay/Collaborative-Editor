from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    language = models.CharField(max_length=50, default='python')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def has_permission(self, user):
        if self.created_by == user:
            return True
        return self.collaborators.filter(user=user).exists()
    
    def get_permission_level(self, user):
        if self.created_by == user:
            return 'owner'
        collab = self.collaborators.filter(user=user).first()
        if collab:
            return collab.permission_level
        return None

class DocumentCollaborator(models.Model):
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('edit', 'Can Edit'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaborated_documents')
    permission_level = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_collaborators')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.document.title} ({self.permission_level})"

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    change_description = models.CharField(max_length=255, blank=True)