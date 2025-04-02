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
    path('asignar-permisos/<str:bd>', views.asignar_permisos, name='asignar_permisos'),
    path('listaroles', views.listaRoles, name='listaRoles'),
    path('formularioRol', views.formularioRol, name='formularioRol'),
    path('crear-rol/', views.crear_rol, name='crear_rol'),
    path('asignarRol', views.asignarRol, name='asignarRol'),
    path('obtenerRoles', views.obtenerRoles, name='obtenerRoles'),
    path('obtenerUsuarios', views.obtenerUsuarios, name='obtenerUsuarios'),
    path('asignar-rol-a-usuario/', views.asignar_rol_a_usuario, name='asignar_rol_a_usuario'),
    path('historialOperaciones', views.historialOperaciones, name='historialOperaciones'),
    path('obtenerTodasOperaciones', views.obtenerTodasOperaciones, name='obtenerTodasOperaciones'),
    path('obtenerFitroTipoOperaciones', views.obtenerFitroTipoOperaciones, name='obtenerFitroTipoOperaciones'),
    path('obtenerFitroFechaOperaciones', views.obtenerFitroFechaOperaciones, name='obtenerFitroFechaOperaciones'),
    path('backupsForm', views.backupsForm, name='backupsForm'),
    path('crear_backup', views.crear_backup, name='crear_backup'),
    path('listaBd', views.listaBd, name='listaBd'),
    #!Aqui inicia las no relacionales
    path('crearBdNoSQL', views.crearBDNoSQL, name='crearBdNoSQL'),
    path('crearUnaNoSQL', views.crearUnaNoSQL, name='crearUnaNoSQL'),
    path('eliminarUnaNoSQL', views.eliminarUnaNoSQL, name='eliminarUnaNoSQL'),
    path('rolesBDNoSQL', views.rolesBDNoSQL, name='rolesBDNoSQL'),
    path('crearRolNoSQL', views.crearRolNoSQL, name='crearRolNoSQL'),
    path('usuariosBDNoSQL', views.usuariosBDNoSQL, name='usuariosBDNoSQL'),
    path('crearUsuarioNoSQL', views.crearUsuarioNoSQL, name='crearUsuarioNoSQL'),
]