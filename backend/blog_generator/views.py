from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

import json
import os

import assemblyai as aai
import openai
from pytube import Youtube

# Create your views here.

@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def genrate_blog(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            # title = yt_title(yt_link)
            # return JsonResponse({'content':yt_link})
        except (KeyError):
            return JsonResponse({'error':'invalid data sent'}, status=400)
        
        # Get video title
        title = yt_title(yt_link)
        
        # Get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': "Failed to get tranascript"}, status=500)
        
        # Use ai to generate blog
        
        # save blog to ai
        
        # return blog as a response
    else:
        return JsonResponse({'error':'invalid request method'}, status=405)
    
def yt_title(link):
    yt = Youtube(link)
    title = yt.title
    return title

def download_audio(link):
    yt = Youtube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api.key = "07bb447d0b2c403dabe29ebf335af6e3"
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    
    return transcriber.text

def generate_blog_from_transcription(transcription):
    pass

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid usernaame or password'
            return render(request, 'login.html', {'error_message':error_message})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']
        
        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message':error_message})
        else:
            error_message = 'Password do not march'
            return render(request, 'signup.html', {'error_message':error_message})
        
        # if form_valid():
        #     pass
        
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')