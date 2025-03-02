from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse

# Create your views here.
def crearBD(request):
    return render(request, 'pages/Formularios/crearBD.html');

def ejecutarCreacion(request):
    if request.method == 'POST':
        database_name = request.POST.get('database_name')
        mdf_name = request.POST.get('mdf_name')
        mdf_file = request.POST.get('mdf_file')
        mdf_size = int(request.POST.get('mdf_size'))  # Asegurarse de convertir a entero
        mdf_growth = int(request.POST.get('mdf_growth'))  # Asegurarse de convertir a entero
        log_name = request.POST.get('log_name')
        log_file = request.POST.get('log_file')
        log_size = int(request.POST.get('log_size'))  # Asegurarse de convertir a entero
        log_growth = int(request.POST.get('log_growth'))  # Asegurarse de convertir a entero

        try:
            with connection.cursor() as cursor:
                query = f"EXEC createNewDataBase '{database_name}', '{mdf_name}', '{mdf_file}', {mdf_size}, {mdf_growth}, '{log_name}', '{log_file}', {log_size}, {log_growth}"
                cursor.execute(query)
            return redirect('result_page', message='La base de datos fue creada exitosamente.')
        except Exception as e:
            return redirect('result_page', message=f'Ocurrió un error: {str(e)}')

    return redirect('result_page', message='Método de solicitud no válido.')


def mostrar_resultado(request, message):
    return render(request, 'pages/Messages/resultado.html', {'message': message})
