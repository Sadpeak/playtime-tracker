from django.shortcuts import render
from django.http import HttpResponse


def home_stats(request):
    return render(request, 'stats_home.html')


def stats_arena(request):
    return render(request, 'stats.html', {'server': 'arena'})


def stats_public(request):
    return render(request, 'stats.html', {'server': 'public'})


def stats_awp(request):
    return render(request, 'stats.html', {'server': 'awp'})


def stats_all(request):
    return render(request, 'stats.html', {'server': 'all'})
