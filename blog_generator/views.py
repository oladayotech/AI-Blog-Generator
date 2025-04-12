from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from urllib.parse import urlparse, parse_qs

import json
import os

import assemblyai as aai
import openai
import yt_dlp
from pytube import YouTube

# Create your views here.

@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            # print(yt_link)
            yt_link = clean_yt_url(yt_link)
            print(yt_link)
        except Exception as e:
            print("Error: {e}")
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)


        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': " Failed to get transcript"}, status=500)


        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': " Failed to generate blog article"}, status=500)

        # # save blog article to database
        # new_blog_article = BlogPost.objects.create(
        #     user=request.user,
        #     youtube_title=title,
        #     youtube_link=yt_link,
        #     generated_content=blog_content,
        # )
        # new_blog_article.save()

        # return blog article as a response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def clean_yt_url(url):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    video_id = query.get("v")
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id[0]}"
    return None
  
# def yt_title(link):
#     try:
#         yt = YouTube(link)
#         title = yt.title
#         print(title)
#         return title
#     except Exception as e:
#         print(f"yt_title error: {e}")
#         return "unknown Title"

def yt_title(link):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            title = info.get('title', 'Unknown Title')
            print(f"Title: {title}")
            return title
        
    except Exception as e:
        print(f"yt_dlp error: {e}")
        return 'Unknown Title'

# def download_audio(link):
#     yt = YouTube(link)
#     video = yt.streams.filter(only_audio=True).first()
#     out_file = video.download(output_path=settings.MEDIA_ROOT)
#     base, ext = os.path.splitext(out_file)
#     new_file = base + '.mp3'
#     os.rename(out_file, new_file)
#     return new_file

def download_audio(link):
    try:
        yt = YouTube(link)
        video = yt.streams.filter(only_audio=True).first()
        if video is None:
            raise Exception("No audio stream found.")
        out_file = video.download(output_path=settings.MEDIA_ROOT)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        return new_file
    except Exception as e:
        print(f"Error downloading audio: {e}")
        raise

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api.key = ""
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    return transcript.text

def generate_blog_from_transcription(transcription):
    openai.api_key = ""

    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1000
    )
    
    generate_content = response.choices[0].text.strip()
    return generate_content

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
