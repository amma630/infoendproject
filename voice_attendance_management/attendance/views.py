import os
import numpy as np
import librosa
import speech_recognition as sr
import pyaudio
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from .models import Attendance
from .forms import VoiceSampleForm
from fuzzywuzzy import process

# 🔹 Check microphone availability
def check_microphone():
    """Checks if the microphone is detected by the system."""
    print("Checking microphone availability...")
    for i in range(pyaudio.PyAudio().get_device_count()):
        print(pyaudio.PyAudio().get_device_info_by_index(i))

check_microphone()

# 🔹 Extract MFCC features for voice comparison
def extract_mfcc(file_path):
    """Extracts MFCC features from an audio file."""
    y, sr = librosa.load(file_path, sr=22050)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)

# 🔹 Compare two voice samples
def compare_voices(sample1, sample2, threshold=0.80):
    """Compares two voice samples using cosine similarity."""
    mfcc1 = extract_mfcc(sample1)
    mfcc2 = extract_mfcc(sample2)
    similarity = np.dot(mfcc1, mfcc2) / (np.linalg.norm(mfcc1) * np.linalg.norm(mfcc2))
    
    print(f"🔎 Voice Match Score: {similarity}")  # Debugging log
    
    return similarity >= threshold

# 🔹 Handle speech recognition with retries
def recognize_speech(prompt, retries=3):
    """Handles speech recognition with retries."""
    recognizer = sr.Recognizer()

    for attempt in range(retries):
        with sr.Microphone() as source:
            print(f"🎤 {prompt} (Attempt {attempt + 1}/{retries})")
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise
            audio = recognizer.listen(source)

        try:
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            print("❌ Could not understand, retrying...")
        except sr.RequestError:
            print("❌ API request failed!")
            break  # Stop retrying if API fails

    return None  # Return None after max retries

@login_required
def upload_voice_sample(request):
    """Allows students to upload their voice samples for attendance verification."""
    if request.user.role != 'student':
        return render(request, 'attendance/unauthorized.html')

    if request.method == 'POST':
        form = VoiceSampleForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = VoiceSampleForm()

    return render(request, 'attendance/upload_voice_sample.html', {'form': form})

def mark_attendance(request):
    """Handles attendance marking through voice authentication."""
    
    if request.user.role != 'teacher':
        return render(request, 'attendance/unauthorized.html')

    messages = []  # Store all messages

    try:
        # 📌 Step 1: Teacher starts attendance
        command = recognize_speech("Teacher, say 'Start Attendance'...")
        messages.append(f"👨‍🏫 Teacher Command: {command}")

        if not command or "start attendance" not in command.lower():
            messages.append("❌ Say 'Start Attendance' to begin!")
            return render(request, 'attendance/mark_attendance.html', {'messages': messages})

        # 📌 Step 2: Capture student name
        recognized_text = recognize_speech("Teacher, please say the student's name...")
        messages.append(f"🎙️ Recognized Student Name: {recognized_text}")

        if not recognized_text:
            messages.append("❌ Could not recognize the student’s name!")
            return render(request, 'attendance/mark_attendance.html', {'messages': messages})

        # Use fuzzy matching to find the closest student name
        student_names = list(CustomUser.objects.filter(role='student').values_list('username', flat=True))
        best_match, score = process.extractOne(recognized_text, student_names)

        messages.append(f"🔍 Best Match: {best_match} (Score: {score}%)")

        if score > 80:
            student = CustomUser.objects.filter(username=best_match, role='student').first()
        else:
            student = None

        if not student:
            messages.append("❌ Student not found!")
            return render(request, 'attendance/mark_attendance.html', {'messages': messages})

        # 📌 Step 3: Validate student's course
        if student.course != request.user.course:
            messages.append(f"❌ {student.username} is not in your course!")
            return render(request, 'attendance/mark_attendance.html', {'messages': messages})

        # 📌 Step 4: Check if attendance is already marked today
        today = date.today()
        if Attendance.objects.filter(student=student, teacher=request.user, date=today).exists():
            messages.append(f"⚠️ {student.username} is already marked present today!")
            return render(request, 'attendance/mark_attendance.html', {'messages': messages})

        # 📌 Step 5: Student confirms attendance
        student_response = recognize_speech(f"Student {student.username}, please say 'Present'...")
        messages.append(f"🎤 Student Response: {student_response}")

        if not student_response or "present" not in student_response.lower():
            messages.append("❌ Student did not confirm attendance!")
            return render(request, 'attendance/mark_attendance.html', {'messages': messages})

        # 📌 Step 6: Match voice sample
        temp_audio_path = "temp_audio.wav"

        # Ensure the recognize_speech function returns audio data if needed
        audio_data = None
        if isinstance(student_response, tuple):
            student_response, audio_data = student_response

        if audio_data:
            with open(temp_audio_path, "wb") as f:
                f.write(audio_data.get_wav_data())

        if student.voice_sample and os.path.exists(student.voice_sample.path):
            if compare_voices(student.voice_sample.path, temp_audio_path):
                Attendance.objects.create(student=student, teacher=request.user, course=student.course, status="Present")
                messages.append(f"✅ Attendance marked for {student.username} ({student.course}) on {today}")
            else:
                messages.append("❌ Voice does not match!")
        else:
            messages.append("❌ No voice sample found for this student.")

        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

    except Exception as e:
        messages.append(f"❌ Error: {str(e)}")

    return render(request, 'attendance/mark_attendance.html', {'messages': messages})

@login_required
def attendance_sheet(request):
    """Displays attendance records filtered by teacher and course."""
    if request.user.role != 'teacher':
        return render(request, 'attendance/unauthorized.html')

    selected_date = request.GET.get('date', str(date.today()))
    attendance_records = Attendance.objects.filter(teacher=request.user, date=selected_date)

    return render(request, 'attendance/attendance_sheet.html', {
        'attendance_records': attendance_records,
        'selected_date': selected_date
    })
