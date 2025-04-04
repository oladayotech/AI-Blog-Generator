from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from pytube import Youtube
import json

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
            return JsonResponse({'content':yt_link})
        except (KeyError):
            return JsonResponse({'error':'invalid data sent'}, status=400)
        
        # Get video title 
        
        # Get transcript
        
        # Use ai to generate blog
        
        # save blog to ai
        
        # return blog as a response
    else:
        return JsonResponse({'error':'invalid request method'}, status=405)

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