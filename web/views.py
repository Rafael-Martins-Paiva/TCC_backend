from django.shortcuts import render
import json

def login_view(request):
    return render(request, 'web/features/login/login.html')

def landing_view(request):
    slide_show_data = {
        'tabs': ["REAL-TIME ANALYTICS", "EASY PROJECTS", "EMAIL NOTIFICATION", "CLOUD SERVERS"],
        'images': json.dumps([
            "/static/web/img/google-icon.png",
            "/static/web/img/facebook-icon.png",
            "/static/web/img/google-icon.png",
            "/static/web/img/facebook-icon.png",
        ])
    }
    return render(request, 'web/features/landing/landing.html', slide_show_data)