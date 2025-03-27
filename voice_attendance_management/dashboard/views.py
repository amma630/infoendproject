from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from attendance.models import Attendance
from tasks.models import Task

@login_required
def dashboard_view(request):
    user = request.user
    attendance = Attendance.objects.filter(student=user).order_by('-date')[:10]
    tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')[:5]

    context = {
        'user': user,
        'attendance': attendance,
        'tasks': tasks
    }
    return render(request, 'dashboard/dashboard.html', context)


from django.shortcuts import render
from tasks.models import Task
from django.utils.timezone import now

def home_view(request):
    return render(request, 'dashboard/home.html')
