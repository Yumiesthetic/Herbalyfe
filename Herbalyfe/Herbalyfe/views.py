from django.shortcuts import render

def home_page(request):
    return render(request, 'home.html')

def profile_page(request):
    return render(request, 'profile.html')

def map_page(request):
    return render(request, 'map.html')
