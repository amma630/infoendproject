from django.db import models
from users.models import CustomUser
from attendance.models import Attendance
from tasks.models import Task

class Dashboard(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="dashboard")
    last_login = models.DateTimeField(auto_now=True)

    def get_attendance_summary(self):
        return Attendance.objects.filter(student=self.user).values('date', 'status')

    def get_task_summary(self):
        return Task.objects.filter(assigned_to=self.user).values('title', 'status')

    def __str__(self):
        return f"{self.user.username}'s Dashboard"
