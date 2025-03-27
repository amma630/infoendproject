import os
import speech_recognition as sr
import librosa
import numpy as np
from django.shortcuts import render
from users.models import CustomUser
from attendance.models import Attendance
from .models import VoiceSample

def extract_mfcc(file_path):
    """Extracts MFCC features from an audio file."""
    y, sr = librosa.load(file_path, sr=22050)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)

def compare_voices(sample1, sample2):
    """Compares two voice samples using cosine similarity."""
    mfcc1 = extract_mfcc(sample1)
    mfcc2 = extract_mfcc(sample2)
    similarity = np.dot(mfcc1, mfcc2) / (np.linalg.norm(mfcc1) * np.linalg.norm(mfcc2))
    return similarity > 0.80  # Acceptable match if similarity is above 80%

def start_attendance(request):
    """Teacher starts voice-based attendance."""
    if not request.user.is_authenticated or request.user.role != 'teacher':
        return render(request, 'voice_assistant/unauthorized.html')

    message = ""

    if request.method == 'POST':
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Teacher, please say the student's name for attendance...")
            audio = recognizer.listen(source)

        try:
            recognized_text = recognizer.recognize_google(audio).lower()
            student = CustomUser.objects.filter(username__iexact=recognized_text, role='student').first()

            if student:
                with sr.Microphone() as source:
                    print(f"Student {student.username}, please say 'present'...")
                    student_audio = recognizer.listen(source)

                temp_audio_path = "temp_audio.wav"
                with open(temp_audio_path, "wb") as f:
                    f.write(student_audio.get_wav_data())

                if student.voice_sample and os.path.exists(student.voice_sample.audio_file.path):
                    if compare_voices(student.voice_sample.audio_file.path, temp_audio_path):
                        Attendance.objects.create(student=student, teacher=request.user, course=student.course, status="Present")
                        message = f"✅ Attendance marked for {student.username}"
                    else:
                        message = "❌ Voice does not match!"
                else:
                    message = "❌ No voice sample found for this student."

                os.remove(temp_audio_path)
            else:
                message = "❌ Student not found!"
        except sr.UnknownValueError:
            message = "❌ Could not understand the audio!"
        except sr.RequestError:
            message = "❌ Speech Recognition API unavailable!"

    return render(request, 'voice_assistant/start_attendance.html', {'message': message})
