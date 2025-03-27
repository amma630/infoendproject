from django.urls import path
from .views import mark_attendance, attendance_sheet
app_name = 'attendance'  # 
urlpatterns = [
    path('mark_attendance/', mark_attendance, name='mark_attendance'),
     path('sheet/', attendance_sheet, name='attendance_sheet'),
]
