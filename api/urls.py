from django.urls import path 
from . import views

urlpatterns = [
    path('today', views.todayGames, name='today'),
    path('probability', views.todayProbabilities, name='probability'),
]
