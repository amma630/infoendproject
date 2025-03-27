from django.urls import path
from .views import start_attendance

urlpatterns = [
    path('start/', start_attendance, name='start_attendance'),
]
