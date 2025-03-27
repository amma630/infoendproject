from django.db import models
from users.models import CustomUser
from datetime import datetime

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.title} - {self.assigned_to.username} - {self.priority}"
