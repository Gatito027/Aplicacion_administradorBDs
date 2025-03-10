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
    
def listaPermisos(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("EXEC sp_ObtenerUsuariosPermisos;")
            response = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute("SELECT name AS BaseDeDatos FROM sys.databases;")
            resultado = cursor.fetchall()
        return render(request, 'pages/views/permisos.html', {'permisos':response, 'dbs':resultado})
    except Exception as e:
        print(e)
        return redirect('result_page', message='Ocurrio un error')
    
def formularioPermisos(request, bd):
    try:
        with connection.cursor() as cursor:
            cursor.execute("EXEC sp_ObtenerUsuariosDeBD @DatabaseName =%s ;", [bd])
            usuarios = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute("exec sp_ObtenerEsquemasDeBD @DatabaseName=%s ;", [bd])
            esquemas = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute("exec sp_ObtenerTablasDeBD @DatabaseName=%s ;", [bd])
            tablas = cursor.fetchall()
        return render(request, 'pages/Formularios/permisosForm.html', {'usuarios':usuarios,'esquemas':esquemas, 'tablas':tablas})
    except Exception as e:
        return redirect('result_page', message='Ocurrio un error')

def asignar_permisos(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        usuario = request.POST.get('usuario')
        tipo = request.POST.get('tipo')
        esquema = request.POST.get('esquemas')
        tabla = request.POST.get('tablas')
        permisos = request.POST.getlist('permisos')  # Lista de permisos seleccionados

        # Determinar el objeto y tipo de objeto
        if tipo == 'Esquema':
            objeto = esquema
            tipo_objeto = 'SCHEMA'
        elif tipo == 'Tabla':
            objeto = tabla
            tipo_objeto = 'TABLE'
        else:
            return JsonResponse({'status': 'error', 'message': 'Tipo de objeto no válido'}, status=400)

        # Llamar al procedimiento almacenado para cada permiso
        try:
            with connection.cursor() as cursor:
                for permiso in permisos:
                    # Asignar el permiso
                    cursor.execute('EXEC AsignarRevocarPermisos %s, %s, %s, %s, %s', [usuario, permiso, 'GRANT', objeto, tipo_objeto])

                # Revocar permisos no seleccionados
                todos_los_permisos = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE']
                permisos_no_seleccionados = set(todos_los_permisos) - set(permisos)
                for permiso in permisos_no_seleccionados:
                    cursor.execute('EXEC AsignarRevocarPermisos %s, %s, %s, %s, %s', [usuario, permiso, 'REVOKE', objeto, tipo_objeto])

            return JsonResponse({'status': 'success', 'message': 'Permisos actualizados correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Si no es POST, redirigir con mensaje de error
    return redirect('result_page', message='Ocurrió un error')

def listaRoles(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("EXEC sp_ObtenerRolesYUsuarios;")
            response = cursor.fetchall()
        return render(request, 'pages/views/roles.html', {'roles':response})
    except Exception as e:
        return redirect('result_page', message='Ocurrio un error')

def formularioRol(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name AS BaseDeDatos FROM sys.databases;")
            resultado = cursor.fetchall()
        return render(request, 'pages/Formularios/crearRolForm.html', {'dbs':resultado})
    except Exception as e:
        return redirect('result_page', message='Ocurrio un error')

def crear_rol(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        base_datos = request.POST.get('bd')
        nombre_rol = request.POST.get('rol_name')
        permisos = request.POST.getlist('permisos')  # Lista de permisos seleccionados

        # Convertir la lista de permisos a una cadena separada por comas
        permisos_str = ','.join(permisos)

        # Llamar al procedimiento almacenado usando EXEC
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                        "EXEC CrearRolConPermisos @base_datos=%s, @nombre_rol=%s, @permisos=%s",
                        [base_datos, nombre_rol, permisos_str]
                    )
            return JsonResponse({'status': 'success', 'message': 'Rol creado exitosamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Si no es POST, renderizar el formulario
    return redirect('result_page', message='Ocurrio un error')

def asignarRol(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name AS BaseDeDatos FROM sys.databases;")
            resultado = cursor.fetchall()
        return render(request, 'pages/Formularios/asignarRolForm.html', {'dbs':resultado})
    except Exception as e:
        return redirect('result_page', message='Ocurrio un error')

def obtenerRoles(request):
    if request.method == 'GET':
        base_datos = request.GET.get('bd')
        try:
            with connection.cursor() as cursor:
                # Ejecutar el procedimiento almacenado para obtener los roles
                cursor.execute('EXEC sp_ObtenerRolesDeBD @DatabaseName = %s;', [base_datos])
                resultado = cursor.fetchall()
                # Extraer el nombre del rol de los resultados
                roles = [row[0] for row in resultado]
                return JsonResponse({'roles': roles})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtenerUsuarios(request):
    if request.method == 'GET':
        base_datos = request.GET.get('bd')
        try:
            with connection.cursor() as cursor:
                # Ejecutar el procedimiento almacenado para obtener los usuarios
                cursor.execute('EXEC sp_ObtenerUsuariosDeBD @DatabaseName = %s;', [base_datos])
                resultado = cursor.fetchall()
                # Extraer el nombre del usuario de los resultados
                usuarios = [row[0] for row in resultado]
                return JsonResponse({'usuarios': usuarios})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def asignar_rol_a_usuario(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        base_datos = request.POST.get('bd')
        nombre_rol = request.POST.get('rol')
        nombre_usuario = request.POST.get('usuario')
        #print(base_datos, nombre_rol, nombre_usuario)

        # Llamar al procedimiento almacenado usando EXEC
        try:
            with connection.cursor() as cursor:
                cursor.execute('EXEC AsignarRolAUsuario @base_datos=%s, @nombre_rol=%s, @nombre_usuario=%s', [base_datos, nombre_rol, nombre_usuario])
            return JsonResponse({'status': 'success', 'message': 'Rol asignado exitosamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Si no es POST, renderizar el formulario
    return redirect('result_page', message='Ocurrio un error')

def historialOperaciones(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("select * from historialOperaciones;")
            response = cursor.fetchall()
        return render(request, 'pages/views/hitorialOperaciones.html',{'operaciones':response} )
    except Exception as e:
        return redirect('result_page', message='Ocurrio un error')
    
def obtenerTodasOperaciones(request):
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                cursor.execute('select * from historialOperaciones;')
                resultado = cursor.fetchall()
                return JsonResponse({'operaciones': resultado})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtenerFitroTipoOperaciones(request):
    if request.method == 'GET':
        filtro = request.GET.get('filtro')
        try:
            with connection.cursor() as cursor:
                cursor.execute('select * from historialOperaciones where operacion= %s;', [filtro])
                resultado = cursor.fetchall()
                return JsonResponse({'operaciones': resultado})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtenerFitroFechaOperaciones(request):
    if request.method == 'GET':
        filtro = request.GET.get('fecha')
        try:
            with connection.cursor() as cursor:
                cursor.execute('select * from historialOperaciones where fecha = %s;', [filtro])
                resultado = cursor.fetchall()
                return JsonResponse({'operaciones': resultado})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)