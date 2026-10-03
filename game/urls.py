from django.urls import path
from . import views

urlpatterns = [
    path('',              views.index,       name='index'),
    path('setup/',        views.setup,       name='setup'),
    path('spielername/',  views.spielername, name='spielername'),
    path('spielen/',      views.spielen,     name='spielen'),
    path('tipp/',         views.tipp_ajax,   name='tipp'),
    path('highscore/',    views.highscore,   name='highscore'),
]
