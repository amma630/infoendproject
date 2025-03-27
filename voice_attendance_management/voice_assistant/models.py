from django.db import models
from users.models import CustomUser

class VoiceSample(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='voice_sample_record')
    audio_file = models.FileField(upload_to='voice_samples/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voice Sample for {self.user.username}"
