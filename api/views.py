from django.shortcuts import render
from django.http import JsonResponse
from .methods import today_objs, today_ids, day_objs, game, get_day_ids

# Create your views here.

def todayGames(request):
    return JsonResponse({'games': [game.game_obj for game in today_objs()]})


