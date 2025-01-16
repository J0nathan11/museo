from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def inicio(request):
    return render(request, 'inicio.html')

#------------------------------INSERTAR DATOS CLIENTE---------------------------------

def agregar_cliente(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula_cli')
        nombre = request.POST.get('nombre_cli')
        apellido = request.POST.get('apellido_cli')
        telefono = request.POST.get('telefono_cli')
        correo = request.POST.get('correo_cli')
        
        query = """
        INSERT INTO clientes (cedula_cli, nombre_cli, apellido_cli, telefono_cli, correo_cli)
        VALUES (%s, %s, %s, %s, %s)
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [cedula, nombre, apellido, telefono, correo])
        
        messages.success(request, 'Cliente registrado y guardado con éxito')
        return redirect('inicio') 

    return render(request, 'agregar_cliente.html')

#---------------------------------VER TALLERES--------------------------------------------------
def listar_talleres(request):
    query = """
    SELECT t.id_tall, t.tema_tall, t.fecha_tall, t.hora_tall, t.estado_tall, o.nombre_org
    FROM talleres t
    JOIN organizador o ON t.fk_id_org = o.id_org
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        talleres = cursor.fetchall()

    talleres_sin_imagen = []
    for taller in talleres:
        id_tall, tema_tall, fecha_tall, hora_tall, estado_tall, nombre_org = taller

        talleres_sin_imagen.append({
            'id_tall': id_tall,
            'tema_tall': tema_tall,
            'fecha_tall': fecha_tall,
            'hora_tall': hora_tall,
            'estado_tall': estado_tall,
            'nombre_org': nombre_org,
        })

    return render(request, 'listar_talleres.html', {'talleres': talleres_sin_imagen})
#--------------------------------LISTAR CLIENTE ORGANIZADOR-----------------------------------------
def listar_clientes_organizador(request):

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    return render(request, 'listar_clientes_organizador.html', {'clientes': clientes})
#---------------------------------EDITAR CLIENTE-------------------------------------------------------------
def editar_cliente(request, id_cli):
    # Realizar la consulta SQL para obtener los datos del cliente
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id_cli = %s", [id_cli])
    cliente = cursor.fetchone()

    if request.method == 'POST':
        # Obtener los datos del formulario
        cedula_cli = request.POST.get('cedula_cli')
        nombre_cli = request.POST.get('nombre_cli')
        apellido_cli = request.POST.get('apellido_cli')
        telefono_cli = request.POST.get('telefono_cli')
        correo_cli = request.POST.get('correo_cli')

        # Actualizar el cliente en la base de datos
        cursor.execute("""
            UPDATE clientes
            SET cedula_cli = %s, nombre_cli = %s, apellido_cli = %s, telefono_cli = %s, correo_cli = %s
            WHERE id_cli = %s
        """, [cedula_cli, nombre_cli, apellido_cli, telefono_cli, correo_cli, id_cli])

        # Redirigir al listado de clientes
        return redirect('listar_clientes_organizador')

    return render(request, 'editar_cliente.html', {'cliente': cliente})

#-------------- -----------------------------------------ELIMINAR CLIENTE-----------------------------------------
def eliminar_cliente(request, id_cli):
    if 'id_org' not in request.session:
        return redirect('login_organizador')

    # Eliminar los registros relacionados en la tabla inscripcion
    query_inscripcion = """
    DELETE FROM inscripcion
    WHERE fk_id_cli = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query_inscripcion, [id_cli])

    # Luego eliminar el cliente
    query_cliente = """
    DELETE FROM clientes
    WHERE id_cli = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query_cliente, [id_cli])

    # Mostrar mensaje de éxito
    messages.success(request, 'Cliente y sus registros relacionados eliminados con éxito.')

    return redirect('listar_clientes_organizador')


#---------------------------------DETALLE TALLER--------------------------------------

def detalle_taller(request, id_tall):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT t.id_tall, t.tema_tall, t.fecha_tall, t.hora_tall, t.estado_tall, d.descripcion_deta
            FROM talleres t
            LEFT JOIN detalles d ON t.id_tall = d.fk_id_tall
            WHERE t.id_tall = %s
        """, [id_tall])
        detalle = cursor.fetchone()

    if detalle:
        id_tall, tema_tall, fecha_tall, hora_tall, estado_tall, descripcion_deta = detalle

        if not descripcion_deta:
            descripcion_deta = "No hay detalles para este taller."

        return render(request, 'detalle_taller.html', {
            'id_tall': id_tall, 
            'tema_tall': tema_tall,
            'fecha_tall': fecha_tall,
            'hora_tall': hora_tall,
            'estado_tall': estado_tall,
            'descripcion_deta': descripcion_deta
        })
    else:
        return render(request, '404.html')



#-----------------------------LOGIN ORGANIZADOR-----------------------------
def login_organizador(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario_org')
        password = request.POST.get('password_org')

        query = """
        SELECT id_org FROM organizador WHERE usuario_org = %s AND password_org = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [usuario, password])
            result = cursor.fetchone()

        if result:
           
            request.session['id_org'] = result[0]  
           
            return redirect('listar_talleres_organizador')  

        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect('login_organizador')  

    return render(request, 'login_organizador.html')

#--------------------------------TALLER ORGANIZADOR-----------------------------------------------------
def listar_talleres_organizador(request):

    if 'id_org' not in request.session:
        return redirect('login_organizador')
     
    id_org = request.session['id_org']

    query = """
    SELECT 
        t.id_tall, 
        t.tema_tall, 
        t.fecha_tall, 
        t.hora_tall, 
        t.estado_tall, 
        o.nombre_org 
    FROM talleres t
    INNER JOIN organizador o ON t.fk_id_org = o.id_org
    WHERE t.fk_id_org = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [id_org])
        talleres = cursor.fetchall()

    return render(request, 'listar_talleres_organizador.html', {'talleres': talleres})

#--------------------------AGREGAR TALLER-----------------------------------------
def agregar_taller(request):
    if request.method == 'POST':
        tema_tall = request.POST.get('tema_tall')
        fecha_tall = request.POST.get('fecha_tall')
        hora_tall = request.POST.get('hora_tall')
        estado_tall = request.POST.get('estado_tall')
        fk_id_org = request.POST.get('fk_id_org')
        descripcion_deta = request.POST.get('descripcion_deta')

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO talleres (tema_tall, fecha_tall, hora_tall, estado_tall, fk_id_org)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_tall
            """, [tema_tall, fecha_tall, hora_tall, estado_tall, fk_id_org])

            id_tall = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO detalles (descripcion_deta, fk_id_tall)
                VALUES (%s, %s)
            """, [descripcion_deta, id_tall])

        messages.success(request, 'Taller agregado con éxito.')
        return redirect('listar_talleres_organizador')

    else:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_org, nombre_org FROM organizador")
            organizadores = cursor.fetchall()
        return render(request, 'agregar_taller.html', {'organizadores': organizadores})

#-------------------------------ELIMINAR-----------------------------------------

def eliminar_taller(request, id_tall):
    if 'id_org' not in request.session:
        return redirect('login_organizador')

    id_org = request.session['id_org']

    query_detalles = """
    DELETE FROM detalles
    WHERE fk_id_tall = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query_detalles, [id_tall])

    query_taller = """
    DELETE FROM talleres
    WHERE id_tall = %s AND fk_id_org = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query_taller, [id_tall, id_org])

    messages.success(request, 'Taller eliminado con éxito.')

    return redirect('listar_talleres_organizador')


#---------------------------------EDITAR TALLER----------------------------------------------
def editar_taller(request, id_tall):

    if 'id_org' not in request.session:
        return redirect('login_organizador')

    query_taller = """
    SELECT id_tall, tema_tall, fecha_tall, hora_tall, estado_tall, fk_id_org
    FROM talleres
    WHERE id_tall = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query_taller, [id_tall])
        result = cursor.fetchone()

    if not result:
        return redirect('listar_talleres_organizador') 

    taller = {
        'id_tall': result[0],
        'tema_tall': result[1],
        'fecha_tall': result[2],
        'hora_tall': result[3],
        'estado_tall': result[4],
        'fk_id_org': result[5],
    }

    query_descripcion = """
    SELECT descripcion_deta FROM detalles
    WHERE fk_id_tall = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query_descripcion, [id_tall])
        descripcion_result = cursor.fetchone()

    if descripcion_result:
        taller['descripcion_deta'] = descripcion_result[0]  

    query_organizadores = """
    SELECT id_org, nombre_org FROM organizador
    """
    with connection.cursor() as cursor:
        cursor.execute(query_organizadores)
        organizadores = cursor.fetchall()

    if request.method == 'POST':
        tema_tall = request.POST['tema_tall']
        fecha_tall = request.POST['fecha_tall']
        hora_tall = request.POST['hora_tall']
        estado_tall = request.POST['estado_tall']
        fk_id_org = request.POST['fk_id_org']
        descripcion_deta = request.POST.get('descripcion_deta')

        query_update = """
        UPDATE talleres
        SET tema_tall = %s, fecha_tall = %s, hora_tall = %s, estado_tall = %s, fk_id_org = %s
        WHERE id_tall = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query_update, [
                tema_tall, fecha_tall, hora_tall, estado_tall, fk_id_org,
                id_tall
            ])

        if descripcion_deta:
            query_detalle_update = """
            INSERT INTO detalles (descripcion_deta, fk_id_tall)
            VALUES (%s, %s)
            ON CONFLICT (fk_id_tall) DO UPDATE SET descripcion_deta = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(query_detalle_update, [descripcion_deta, id_tall, descripcion_deta])

        messages.success(request, 'Taller actualizado correctamente.')
        return redirect('listar_talleres_organizador')

    return render(request, 'editar_taller.html', {'taller': taller, 'organizadores': organizadores})

#----------------------------INSCRIPCION----------------------------------
from datetime import date

def inscripcion_taller(request, id_tall):
    if request.method == 'POST':
        cedula_cli = request.POST.get('cedula_cli')

        # Verificar si el cliente existe
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_cli FROM clientes WHERE cedula_cli = %s", [cedula_cli])
            cliente = cursor.fetchone()

        if cliente:
            id_cli = cliente[0]

            # Registrar la inscripción
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO inscripcion (fecha_ins, fk_id_cli, fk_id_tall)
                    VALUES (%s, %s, %s)
                """, [date.today(), id_cli, id_tall])

            messages.success(request, 'Inscripción realizada con éxito.')
            return redirect('listar_talleres') 
        else:
            messages.error(request, 'No se encontró un cliente con la cédula proporcionada.')

    with connection.cursor() as cursor:
        cursor.execute("SELECT tema_tall FROM talleres WHERE id_tall = %s", [id_tall])
        taller = cursor.fetchone()

    if not taller:
        messages.error(request, 'El taller no existe.')
        return redirect('listar_talleres')

    tema_tall = taller[0]

    return render(request, 'inscripcion_taller.html', {'tema_tall': tema_tall, 'id_tall': id_tall})

#-------------------------------------CONSULTAS DE INSCRIPCIONES POR CLIENTE---------------------------

def consultar_inscripcion(request):
    if request.method == 'POST':
        cedula_cli = request.POST.get('cedula_cli')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_cli FROM clientes WHERE cedula_cli = %s
            """, [cedula_cli])
            cliente = cursor.fetchone()

        if cliente:
            return redirect('listar_inscripcion', cedula_cli=cedula_cli)
        else:
            messages.error(request, 'No se encontró un cliente con la cédula proporcionada.')

    return render(request, 'consulta_inscripcion.html')


def listar_inscripcion(request, cedula_cli):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_cli, nombre_cli FROM clientes WHERE cedula_cli = %s
        """, [cedula_cli])
        cliente = cursor.fetchone()

    if cliente:
        id_cli, nombre_cli = cliente

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT t.tema_tall, t.fecha_tall, t.hora_tall, i.fecha_ins
                FROM inscripcion i
                JOIN talleres t ON i.fk_id_tall = t.id_tall
                WHERE i.fk_id_cli = %s
            """, [id_cli])
            inscripciones = cursor.fetchall()

        return render(request, 'listar_inscripcion.html', {
            'inscripciones': inscripciones,
            'cedula_cli': cedula_cli,
            'nombre_cli': nombre_cli
        })
    else:
        messages.error(request, 'No se encontró un cliente con la cédula proporcionada.')
        return redirect('consultar_inscripcion')
