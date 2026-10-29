
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def awareness(request):
    return render(request, "awareness.html")
