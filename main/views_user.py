from django.contrib.auth.models import User
from django.shortcuts import render

def user_profile(request):
    return render(request, "user_profile.html")