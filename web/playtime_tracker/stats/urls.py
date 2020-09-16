from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_stats, name='home_stats'),
    path('arena/', views.stats_arena, name='stats_arena'),
    path('public/', views.stats_public, name='stats_public'),
    path('awp/', views.stats_awp, name='stats_awp'),
    path('all/', views.stats_all, name='stats_all'),
]
