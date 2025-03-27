from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required

@login_required
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('task_list')
