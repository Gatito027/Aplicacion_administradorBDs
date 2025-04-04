from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

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
                    #return redirect('result_page', message='Base de datos creada exitosamente.')
                    return JsonResponse({'status': 'success', 'message': 'Base de datos creada exitosamente.'})
                elif return_code == 20:
                    #return redirect('result_page', message='La base de datos ya existe.')
                    return JsonResponse({'status': 'success', 'message': 'La base de datos ya existe.'})
                else:
                    return JsonResponse({'status': 'success', 'message': 'Error al crear la base de datos.'})
                    #return redirect('result_page', message='Error al crear la base de datos.')
        except Exception as e:
            # Manejar cualquier excepción que ocurra durante la ejecución
            #return redirect('result_page', message=f'Ocurrió un error: {str(e)}')
            return JsonResponse({'status': 'success', 'message': f'Ocurrió un error: {str(e)}'})

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
        return render(request, 'pages/Formularios/permisosForm.html', {'usuarios':usuarios,'esquemas':esquemas, 'tablas':tablas, 'bd':[bd], })
    except Exception as e:
        return redirect('result_page', message='Ocurrio un error')

def asignar_permisos(request, bd):
    if request.method == 'POST':
        # Obtener los datos del formulario
        usuario = request.POST.get('usuario')
        tipo = request.POST.get('tipo')
        esquema = request.POST.get('esquemas')
        tabla = request.POST.get('tablas')
        permisos = request.POST.getlist('permisos')  # Lista de permisos seleccionados

        # Validar que se haya seleccionado un usuario y un tipo
        if not usuario or not tipo:
            return JsonResponse({'status': 'error', 'message': 'Usuario y tipo son obligatorios'}, status=400)

        # Determinar el objeto y tipo de objeto
        if tipo == 'Esquema':
            objeto = esquema
            tipo_objeto = 'SCHEMA'
        elif tipo == 'Tabla':
            objeto = tabla
            tipo_objeto = 'TABLE'
        else:
            return JsonResponse({'status': 'error', 'message': 'Tipo de objeto no válido'}, status=400)

        # Validar que se haya seleccionado un objeto (esquema o tabla)
        if not objeto:
            return JsonResponse({'status': 'error', 'message': 'Debes seleccionar un esquema o una tabla'}, status=400)

        # Validar que se haya seleccionado al menos un permiso
        if not permisos:
            return JsonResponse({'status': 'error', 'message': 'Debes seleccionar al menos un permiso'}, status=400)

        # Convertir la lista de permisos en una cadena separada por comas
        permisos_str = ','.join(permisos)

        # Depuración: Imprimir los valores que se enviarán al SP
        print(f"Valores enviados al SP: usuario={usuario}, permisos={permisos_str}, accion=GRANT, objeto={objeto}, tipo_objeto={tipo_objeto}, nombre_bd={bd}")

        # Llamar al procedimiento almacenado
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC AsignarRevocarPermisos @usuario=%s, @permisos=%s, @accion=%s, @objeto=%s, @tipo_objeto=%s, @nombre_bd=%s",
                    [usuario, permisos_str, 'GRANT', objeto, tipo_objeto, bd]
                )
                todos_los_permisos = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE']
                permisos_no_seleccionados = set(todos_los_permisos) - set(permisos)
                for permiso in permisos_no_seleccionados:
                    cursor.execute('EXEC AsignarRevocarPermisos %s, %s, %s, %s, %s, %s', 
                    [usuario, permiso, 'REVOKE', objeto, tipo_objeto, bd])
                return JsonResponse({'status': 'success', 'message': 'Permisos asignados correctamente'})
        except Exception as e:
            # Depuración: Imprimir el error
            print(f"Error al ejecutar el procedimiento almacenado: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Error al ejecutar el procedimiento almacenado: {str(e)}'}, status=500)

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

def backupsForm(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name AS BaseDeDatos FROM sys.databases WHERE database_id > 4;")
            resultado = cursor.fetchall()
        return render(request, 'pages/Formularios/backupsForm.html', {'dbs':resultado})
    except Exception as e:
        print(e)
        return redirect('result_page', message='Ocurrio un error')

def crear_backup(request):
    if request.method == 'POST':
        bd = request.POST['bd']
        file = request.POST['file']
        tipo = 'completo'
        print(bd, file, tipo)
        try:
            #with connection.cursor() as cursor:
            #    sql = "BACKUP DATABASE [%s] TO DISK = '%s\\test.bak'" % (bd, file)
            #    cursor.execute(sql)
            with connection.cursor() as cursor:
                cursor.execute("EXEC sp_CrearBackup @NombreBaseDatos = %s, @Ubicacion = %s,@TipoBackup = %s", 
                    [str(bd), str(file), str(tipo)])
                resultado = cursor.fetchall()
                print(resultado)
            return JsonResponse({"mensaje": "Backup creado exitosamente"}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    # Obtener lista de bases de datos (esto dependerá de cómo obtienes las bases de datos)
    return redirect('result_page', message='Ocurrio un error')

def listaBd(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name AS BaseDeDatos FROM sys.databases WHERE database_id > 4;")
            resultado = cursor.fetchall()
        return render(request, 'pages/views/listaBds.html', {'dbs':resultado})
    except Exception as e:
        return redirect('result_page', message='Ocurrio un error')
    
#!NoSQL
# URL base para las solicitudes externas
api = 'http://localhost:3000'

def crearBDNoSQL(request):
    try:
        # Obtener las bases de datos mediante la función listabdNoSQL
        bd = listabdNoSQL()
        if isinstance(bd, dict) and "error" in bd:
            # Si hubo un error, redirigir a una página de error con mensaje
            return redirect('result_page', message=bd["error"])
        # Renderizar la plantilla con los datos obtenidos
        return render(request, 'pages/Formularios/CrearBDNoSQL.html', {'dbs': bd})
    except Exception as e:
        # Manejo de errores genéricos
        return redirect('result_page', message=f'Error inesperado: {str(e)}')

def listabdNoSQL():
    try:
        # Hacer la solicitud GET a la ruta externa
        response = requests.get(f'{api}/list-dbs')

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Obtener los datos de la respuesta
            return response.json()  # Suponiendo que el endpoint retorna JSON
        else:
            # Manejar el caso de error
            return {"error": f"Error en la solicitud: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        # Manejar excepciones de la solicitud
        return {"error": str(e)}

def crearUnaNoSQL(request):
    if request.method == 'POST':
        bd_name = request.POST.get('database_name') 
        if not bd_name:
            # Manejar el caso en que no se proporcione un nombre de base de datos
            return JsonResponse({"error": "El nombre de la base de datos es requerido."}, status=400)
        try:
            # Crear el JSON que se enviará en el cuerpo de la solicitud
            payload = {"dbName": bd_name}
            # Realizar la solicitud POST al endpoint
            response = requests.post(f'{api}/create-db', json=payload)
            if response.status_code == 200:
                # Obtener los datos de la respuesta y retornarlos como JSON
                return JsonResponse(response.json(), status=200)
            else:
                # Manejar el caso de error en la solicitud
                return JsonResponse({"error": f"Error en la solicitud: {response.status_code}"}, status=response.status_code)
        except requests.exceptions.RequestException as e:
            # Manejar excepciones de la solicitud
            return JsonResponse({"error": f"Excepción en la solicitud: {str(e)}"}, status=500)
    else:
        # Manejar el caso en que el método no sea POST
        return JsonResponse({"error": "Método no permitido, se requiere POST."}, status=405)
    
def eliminarUnaNoSQL(request):
    if request.method == 'POST':
        bd_name = request.POST.get('database_name') 
        if not bd_name:
            # Manejar el caso en que no se proporcione un nombre de base de datos
            return JsonResponse({"error": "El nombre de la base de datos es requerido."}, status=400)
        try:
            # Crear el JSON que se enviará en el cuerpo de la solicitud
            payload = {"dbName": bd_name}
            # Realizar la solicitud POST al endpoint
            response = requests.post(f'{api}/delete-db', json=payload)
            if response.status_code == 200:
                # Obtener los datos de la respuesta y retornarlos como JSON
                return JsonResponse(response.json(), status=200)
            else:
                # Manejar el caso de error en la solicitud
                return JsonResponse({"error": f"Error en la solicitud: {response.status_code}"}, status=response.status_code)
        except requests.exceptions.RequestException as e:
            # Manejar excepciones de la solicitud
            return JsonResponse({"error": f"Excepción en la solicitud: {str(e)}"}, status=500)
    else:
        # Manejar el caso en que el método no sea POST
        return JsonResponse({"error": "Método no permitido, se requiere POST."}, status=405)
    
def rolesBDNoSQL(request):
    try:
        bd = listabdNoSQL()
        if isinstance(bd, dict) and "error" in bd:
            # Si hubo un error, redirigir a una página de error con mensaje
            return redirect('result_page', message=bd["error"])
        roles = listaRolesNoSQL()
        if isinstance(roles, dict) and "error" in roles:
            # Si hubo un error, redirigir a una página de error con mensaje
            return redirect('result_page', message=roles["error"])
        # Renderizar la plantilla con los datos obtenidos
        return render(request, 'pages/Formularios/RolesBDNoSQL.html', {"roles":roles, "dbs":bd})
    except Exception as e:
        # Manejo de errores genéricos
        return redirect('result_page', message=f'Error inesperado: {str(e)}')
    
def listaRolesNoSQL():
    try:
        # Hacer la solicitud GET a la ruta externa
        response = requests.get(f'{api}/list-roles')
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Obtener los datos de la respuesta
            return response.json()  # Suponiendo que el endpoint retorna JSON
        else:
            # Manejar el caso de error
            return {"error": f"Error en la solicitud: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        # Manejar excepciones de la solicitud
        return {"error": str(e)}
    
def crearRolNoSQL(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        rol_name = request.POST.get('rol_name')
        database_name = request.POST.get('bd')
        permisos_seleccionados = request.POST.getlist('permisos')  # Obtener permisos seleccionados
        if not rol_name or not database_name or not permisos_seleccionados:
            return JsonResponse({"error": "Todos los campos son requeridos (roleName, dbName, permissions)."}, status=400)
        try:
            # Construir la estructura de permisos en el formato requerido
            permissions = [
                {
                    "resource": {
                        "db": database_name,
                        "collection": ""
                    },
                    "actions": permisos_seleccionados
                }
            ]
            # Crear el JSON de la solicitud
            payload = {
                "roleName": rol_name,
                "dbName": database_name,
                "permissions": permissions
            }
            # Enviar la solicitud POST al endpoint
            response = requests.post(f'{api}/create-role', json=payload)
            if response.status_code == 200:
                return JsonResponse(response.json(), status=200)
            else:
                return JsonResponse({"error": f"Error en la solicitud: {response.status_code}"}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Excepción en la solicitud: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Método no permitido, se requiere POST."}, status=405)
    
def usuariosBDNoSQL(request):
    try:
        usuarios = listaUsuariosNoSQL()
        if isinstance(usuarios, dict) and "error" in usuarios:
            # Si hubo un error, redirigir a una página de error con mensaje
            return redirect('result_page', message=usuarios["error"])
        roles = listaRolesNoSQL()
        if isinstance(roles, dict) and "error" in roles:
            # Si hubo un error, redirigir a una página de error con mensaje
            return redirect('result_page', message=roles["error"])
        bd = listabdNoSQL()
        if isinstance(bd, dict) and "error" in bd:
            # Si hubo un error, redirigir a una página de error con mensaje
            return redirect('result_page', message=bd["error"])
        # Renderizar la plantilla con los datos obtenidos
        return render(request, 'pages/Formularios/usuariosBDNoSQL.html', {"usuarios":usuarios, "roles":roles, "dbs":bd})
    except Exception as e:
        # Manejo de errores genéricos
        return redirect('result_page', message=f'Error inesperado: {str(e)}')
    
def listaUsuariosNoSQL():
    try:
        # Hacer la solicitud GET a la ruta externa
        response = requests.get(f'{api}/list-users-collection')
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Obtener los datos de la respuesta
            return response.json()  # Suponiendo que el endpoint retorna JSON
        else:
            # Manejar el caso de error
            return {"error": f"Error en la solicitud: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        # Manejar excepciones de la solicitud
        return {"error": str(e)}

def crearUsuarioNoSQL(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.POST.get('username')
        password = request.POST.get('password')
        roles = []
        
        # Procesar los roles asignados
        index = 0
        while True:
            role_key = f'roles[{index}][role]'
            db_key = f'roles[{index}][db]'
            
            if role_key not in request.POST or db_key not in request.POST:
                break
                
            roles.append({
                "name": request.POST.get(role_key),
                "db": request.POST.get(db_key)
            })
            index += 1

        if not username or not password or not roles:
            return JsonResponse({
                "error": "Todos los campos son requeridos (username, password, roles)."
            }, status=400)

        try:
            # Construir el payload en el formato requerido
            payload = {
                "dbName": roles[0]['db'],  # Tomamos la primera BD como principal
                "username": username,
                "password": password,
                "roles": roles
            }

            # Enviar la solicitud POST al endpoint de MongoDB
            response = requests.post(
                f'{api}/create-user',
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                return JsonResponse(response.json(), status=200)
            else:
                return JsonResponse({
                    "error": f"Error en la solicitud a MongoDB: {response.status_code}",
                    "details": response.text
                }, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({
                "error": "Excepción en la conexión con MongoDB",
                "details": str(e)
            }, status=500)
    else:
        return JsonResponse({
            "error": "Método no permitido, se requiere POST."
        }, status=405)