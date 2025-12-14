"""
Views for the config project.
"""
from django.shortcuts import render


def home(request):
    """
    Home page view with dark theme dashboard.
    """
    return render(request, 'home.html')
