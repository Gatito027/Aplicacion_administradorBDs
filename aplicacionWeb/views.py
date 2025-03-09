from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def crearBD(request):
    return render(request, 'pages/Formularios/crearBD.html')

def ejecutarCreacion(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        database_name = request.POST.get('database_name')
        mdf_name = request.POST.get('mdf_name')
        mdf_file = request.POST.get('mdf_file')
        log_name = request.POST.get('log_name')
        log_file = request.POST.get('log_file')

        # Parámetros opcionales (pueden ser None si no se proporcionan)
        mdf_size = request.POST.get('mdf_size')
        mdf_growth = request.POST.get('mdf_growth')
        log_size = request.POST.get('log_size')
        log_growth = request.POST.get('log_growth')
        secondary_filegroups = request.POST.get('secondary_filegroups')  # Filegroups secundarios (opcional)

        # Convertir a enteros si están presentes
        mdf_size = int(mdf_size) if mdf_size else None
        mdf_growth = int(mdf_growth) if mdf_growth else None
        log_size = int(log_size) if log_size else None
        log_growth = int(log_growth) if log_growth else None

        try:
            with connection.cursor() as cursor:
                # Construir la llamada al procedimiento almacenado dinámicamente
                sql = """
                    DECLARE @ReturnCode INT;
                    EXEC @ReturnCode = createNewDataBase 
                        @DataBaseName=%s, @mdfName=%s, @mdfFile=%s,
                        @logName=%s, @logFile=%s
                """
                params = [database_name, mdf_name, mdf_file, log_name, log_file]

                # Agregar parámetros opcionales si están presentes
                if mdf_size is not None:
                    sql += ", @mdfSize=%s"
                    params.append(mdf_size)
                if mdf_growth is not None:
                    sql += ", @mdfGrowth=%s"
                    params.append(mdf_growth)
                if log_size is not None:
                    sql += ", @logSize=%s"
                    params.append(log_size)
                if log_growth is not None:
                    sql += ", @logGrowth=%s"
                    params.append(log_growth)
                if secondary_filegroups:
                    sql += ", @SecondaryFilegroups=%s"
                    params.append(secondary_filegroups)

                # Finalizar la consulta SQL
                sql += "; SELECT @ReturnCode AS ReturnCode;"

                # Ejecutar la consulta SQL con los parámetros
                cursor.execute(sql, params)
                
                # Obtener el código de retorno del procedimiento almacenado
                result = cursor.fetchone()
                return_code = result[0] if result else None

                # Manejar el resultado según el código de retorno
                if return_code == 0:
                    return redirect('result_page', message='Base de datos creada exitosamente.')
                elif return_code == 20:
                    return redirect('result_page', message='La base de datos ya existe.')
                else:
                    return redirect('result_page', message='Error al crear la base de datos.')
        except Exception as e:
            # Manejar cualquier excepción que ocurra durante la ejecución
            return redirect('result_page', message=f'Ocurrió un error: {str(e)}')

    # Redirigir si el método no es POST
    return redirect('result_page', message='Método de solicitud no válido.')


def mostrar_resultado(request, message):
    return render(request, 'pages/Messages/resultado.html', {'message': message})

def getionUsuarios(request):
    return render(request, 'pages/views/UsuariosInicio.html')

def listaUsuarios(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("EXEC consultarLoginsUsuarios;")
            usuarios = cursor.fetchall()
        return render(request, 'pages/views/LoginsUsuarios.html', {'usuarios':usuarios})
    except Exception as e:
        return redirect('result_page', message='Ocurrio un error')

def formularioLogin(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name AS BaseDeDatos FROM sys.databases;")
            resultado = cursor.fetchall()
        return render(request, 'pages/Formularios/usuariosLoginsform.html', {'dbs':resultado})
    except Exception as e:
        return redirect('result_page', message='Ocurrio un error')

@csrf_exempt
def CrearLoginUsuarioView(request):
    if request.method == 'POST':
        loginName = request.POST.get('loginName')
        loginPassword = request.POST.get('loginPassword')
        usuarios = []
        # Recoger todos los usuarios y bases de datos enviados
        i = 0
        while True:
            userName = request.POST.get(f'userName{i}')
            bd = request.POST.get(f'bd{i}')
            if not userName or not bd:
                break
            usuarios.append((userName, bd))
            i += 1

        try:
            # Ejecutar el procedimiento almacenado para cada usuario
            for userName, bd in usuarios:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "EXEC CrearLoginYUsuario @loginName=%s, @loginPassword=%s, @userName=%s, @bd=%s",
                        [loginName, loginPassword, userName, bd]
                    )
            return JsonResponse({'status': 'success', 'message': 'Login y usuarios creados exitosamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)