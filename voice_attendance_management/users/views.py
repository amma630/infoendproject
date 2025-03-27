from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from .forms import StudentRegistrationForm, TeacherRegistrationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'
            user.save()
            return redirect('login')  # Redirect to login after registration
    else:
        form = StudentRegistrationForm()
    return render(request, 'users/student_register.html', {'form': form})

def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'teacher'
            user.save()
            return redirect('login')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'users/teacher_register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def dashboard(request):
    return render(request, 'users/dashboard.html', {'user': request.user})
def user_logout(request):
    logout(request)
    return redirect('logout_page')  