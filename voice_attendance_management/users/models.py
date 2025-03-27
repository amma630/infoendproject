from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='student')
    course = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')],default='male')
    voice_sample = models.FileField(upload_to='voice_samples/', blank=True, null=True)  # Only for students

    def is_student(self):
        return self.role == 'student'

    def is_teacher(self):
        return self.role == 'teacher'
