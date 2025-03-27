from django import forms
from .models import CustomUser

class VoiceSampleForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['voice_sample']
