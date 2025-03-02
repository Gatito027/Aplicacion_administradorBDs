from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.crearBD, name='crearBdView'),
    path('/newdatabase', views.ejecutarCreacion, name='crearBd'),
    path('resultado/<str:message>/', views.mostrar_resultado, name='result_page'),
]