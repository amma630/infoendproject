from django.db import models
from datetime import datetime
from users.models import CustomUser

class Attendance(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendances', null=True, blank=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='teacher_attendances', null=True, blank=True)
    course = models.CharField(max_length=100, blank=True, null=True)  # Allow blank course if needed
    date = models.DateField(default=datetime.today)  # Default to today's date
    time = models.TimeField(default=datetime.now)  # Default to current time
    status = models.CharField(max_length=10, choices=[("Present", "Present"), ("Absent", "Absent")], default="Absent")

    def __str__(self):
        return f"{self.student.username if self.student else 'Unknown'} - {self.course} - {self.date} - {self.status}"
