from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class StudentRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=100)
    course = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')])
    voice_sample = forms.FileField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'password1', 'password2', 'course', 'gender', 'voice_sample']

class TeacherRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=100)
    course = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')])

    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'password1', 'password2', 'course', 'gender']
