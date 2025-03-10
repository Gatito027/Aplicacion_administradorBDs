from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.crearBD, name='crearBdView'),
    path('newdatabase', views.ejecutarCreacion, name='crearBd'),
    path('resultado/<str:message>/', views.mostrar_resultado, name='result_page'),
    path('gestionusuarios', views.getionUsuarios, name='gestionUsuarios'),
    path('listausuarios', views.listaUsuarios, name='listaUsuarios'),
    path('fromularioLogin', views.formularioLogin, name='formularioLogin'),
    path('ejecutarCrearUsuario', views.CrearLoginUsuarioView, name='ejecutarCrearUsuario'),
    path('listapermisos', views.listaPermisos, name='listaPermisos'),
    path('formularioPermisos/<str:bd>', views.formularioPermisos,name='formularioPermisos'),
    path('asignar-permisos/', views.asignar_permisos, name='asignar_permisos'),
]