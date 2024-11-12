import random
import datetime
import calendar
import os

# Listas de nombres y programas
nombres_reflexion = []
nombres_canto = []
nombres_restantes = []
nombres_programas = []
departamentos = ["Departamento A", "Departamento B", "Departamento C"]

# Histórico de participaciones
historico_participantes = {}

# Cargar datos desde archivos .txt
def cargar_lista(nombre_archivo, lista):
    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                lista.append(linea.strip())
    except FileNotFoundError:
        with open(nombre_archivo, 'w') as archivo:
            pass  # Si el archivo no existe, lo creamos vacío

cargar_lista("nombres_reflexion.txt", nombres_reflexion)
cargar_lista("nombres_canto.txt", nombres_canto)
cargar_lista("nombres_restantes.txt", nombres_restantes)
cargar_lista("nombres_programas.txt", nombres_programas)

# Guardar listas en archivos .txt
def guardar_lista(nombre_archivo, lista):
    with open(nombre_archivo, 'w') as archivo:
        for item in lista:
            archivo.write(item + "\n")

# Guardar histórico de participantes
def guardar_historico():
    with open("historico_participantes.txt", 'w') as archivo:
        for nombre, data in historico_participantes.items():
            archivo.write(f"{nombre},{data['rol']},{data['fecha']}\n")

# Cargar histórico de participantes


def cargar_historico():
    try:
        with open("historico_participantes.txt", 'r') as archivo:
            for linea in archivo:
                nombre, rol, fecha = linea.strip().split(',')
                try:
                    # Intentar con fecha y hora con milisegundos
                    fecha_datetime = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    try:
                        # Intentar con fecha y hora sin milisegundos
                        fecha_datetime = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # Intentar solo con fecha
                        fecha_datetime = datetime.datetime.strptime(fecha, "%Y-%m-%d")
                
                historico_participantes[nombre] = {'rol': rol, 'fecha': fecha_datetime}
    except FileNotFoundError:
        pass

# Ejecutar la función para cargar el historial
cargar_historico()

# Verificar si el nombre cumple con el límite de programas entre participaciones
def verificar_historial(nombre, rol, programas_entre):
    if nombre in historico_participantes:
        ultima_fecha = historico_participantes[nombre]['fecha']
        diferencia = (datetime.datetime.now().date() - ultima_fecha.date()).days // 7
        return diferencia >= programas_entre
    return True

# Actualizar el historial de participación
def actualizar_historial(nombre, rol, fecha):
    historico_participantes[nombre] = {'rol': rol, 'fecha': fecha}
    guardar_historico()

# Seleccionar nombres sin repetir
def asignar_participantes():
    if len(nombres_restantes) < 6:
        print("No hay suficientes nombres en la lista 'restantes' para completar el programa.")
        return None

    random.shuffle(nombres_restantes)

    seleccionados = {}

    # Seleccionar para "Ejercicio de Canto" y eliminar de la lista para evitar duplicados
    seleccionados["Ejercicio de Canto"] = next(
        (nombre for nombre in nombres_canto if verificar_historial(nombre, "Ejercicio de Canto", 2)),
        None
    )
    if seleccionados["Ejercicio de Canto"]:
        nombres_canto.remove(seleccionados["Ejercicio de Canto"])

    # Seleccionar para "Reflexión" y eliminar de la lista para evitar duplicados
    seleccionados["Reflexión"] = next(
        (nombre for nombre in nombres_reflexion if verificar_historial(nombre, "Reflexión", 4)),
        None
    )
    if seleccionados["Reflexión"]:
        nombres_reflexion.remove(seleccionados["Reflexión"])

    # Seleccionar nombres restantes para otros roles y eliminarlos después de asignar
    for rol in ["Dirigir", "Dinámica", "Bando de Oración", "Matutina", "Ejercicio Bíblico"]:
        seleccionados[rol] = next(
            (nombre for nombre in nombres_restantes if verificar_historial(nombre, rol, 2)),
            None
        )
        if seleccionados[rol]:
            nombres_restantes.remove(seleccionados[rol])

    if not all(seleccionados.values()):
        print("No hay suficientes nombres disponibles para las restricciones de repetición.")
        return None

    # Actualizar historial con la fecha actual
    for rol, nombre in seleccionados.items():
        if nombre:
            actualizar_historial(nombre, rol, datetime.datetime.now())

    return seleccionados

    fecha_actual = datetime.datetime.now().date()
    for rol, nombre in seleccionados.items():
        actualizar_historial(nombre, rol, fecha_actual)

    return seleccionados

# Agregar nombres a una lista específica
def agregar_nombres(lista, archivo):
    nombres = input("Ingrese nombres separados por comas: ")
    nombres_lista = [nombre.strip() for nombre in nombres.split(',') if nombre.strip()]
    lista.extend(nombres_lista)
    guardar_lista(archivo, lista)
    print(f"Nombres agregados exitosamente a {archivo}.")

# Función para mostrar y seleccionar fechas de sábados disponibles
def obtener_sabados_libres(mes, año):
    sabados_libres = []
    fecha_actual = datetime.date(mes, año, 1)
    while fecha_actual.month == mes:
        if fecha_actual.weekday() == 5:  # Es sábado
            if not verificar_fecha_programa(fecha_actual):
                sabados_libres.append(fecha_actual)
        fecha_actual += datetime.timedelta(days=1)
    return sabados_libres

# Verificar si ya existe un programa para una fecha dada
def verificar_fecha_programa(fecha):
    if os.path.exists("fechas_programas.txt"):
        with open("fechas_programas.txt", 'r') as archivo:
            for linea in archivo:
                if fecha.strftime("%Y-%m-%d") in linea:
                    return True
    return False

# Función para crear y actualizar archivos de programas
def generar_programa(fecha, programa_titulo, participantes, hora_inicio, es_misionero=False):
    nombre_archivo = f"aa_{programa_titulo}_{fecha}.txt"
    with open(nombre_archivo, 'w') as archivo:
        archivo.write(f"{programa_titulo} - {fecha}\n".center(50))
        archivo.write("="*50 + "\n")
        
        if es_misionero:
            archivo.write("Este sábado se realizará obra misionera.\n")
            archivo.write("Participantes deben estar preparados para actividades de servicio.\n")
            print(f"Programa misionero guardado en {nombre_archivo}")
            return

        hora_actual = datetime.datetime.strptime(hora_inicio, "%H:%M")
        participaciones = [
            ("Ejercicio de Canto", 15),
            ("Dirigir", 5),
            ("Dinámica", 20),
            ("Bando de Oración", 10),
            ("Matutina", 20),
            ("Ejercicio Bíblico", 20),
            ("Reflexión", random.randint(15, 20)),
        ]
        for participacion, duracion in participaciones:
            encargado = participantes[participacion]
            hora_fin = hora_actual + datetime.timedelta(minutes=duracion)
            archivo.write(f"{hora_actual.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')} - {participacion} - {encargado}\n")
            hora_actual = hora_fin
    print(f"Programa guardado en {nombre_archivo}")

# Función para editar un programa existente
def editar_programa():
    fecha = input("Ingrese la fecha del programa a editar (YYYY-MM-DD): ")
    fecha_obj = datetime.datetime.strptime(fecha, "%d-%m-%Y")
    nombre_programa = input("Ingrese el título del programa: ")
    nombre_archivo = f"{nombre_programa}_{fecha}.txt"

    if not os.path.exists(nombre_archivo):
        print("El archivo del programa no existe.")
        return

    with open(nombre_archivo, 'r') as archivo:
        contenido = archivo.readlines()

    print("\n--- Opciones de edición ---")
    print("1. Cambiar título")
    print("2. Cambiar hora de inicio")
    print("3. Intercambiar encargados en participaciones")
    opcion = input("Seleccione una opción: ")

    if opcion == '1':
        nuevo_titulo = input("Ingrese el nuevo título: ")
        contenido[0] = f"{nuevo_titulo} - {fecha}\n".center(50)
    elif opcion == '2':
        nueva_hora = input("Ingrese la nueva hora de inicio (HH:MM): ")
        contenido[1] = f"Hora de inicio: {nueva_hora}\n"
    elif opcion == '3':
        participacion = input("Ingrese la participación a modificar (Ejemplo: Dirigir): ")
        nuevo_encargado = input("Ingrese el nombre del nuevo encargado: ")
        for i, linea in enumerate(contenido):
            if participacion in linea:
                partes = linea.split(" - ")
                partes[-1] = nuevo_encargado + "\n"
                contenido[i] = " - ".join(partes)
                break
    else:
        print("Opción no válida.")
        return

    # Guardar los cambios en el archivo
    with open(nombre_archivo, 'w') as archivo:
        archivo.writelines(contenido)
    print(f"Programa actualizado en {nombre_archivo}")


def existente_fecha():
    fecha_input = input("Ingrese la fecha del programa (YYYY-MM-DD): ")
    try:
        fecha = datetime.datetime.strptime(fecha_input, "%Y-%m-%d").date()
    except ValueError:
        print("Formato de fecha incorrecto. Intente nuevamente.")
        return

    if verificar_fecha_programa(fecha):
        print("Ya existe un programa para esta fecha.")
        return

    titulo_programa = input("Ingrese el título del programa: ")
    opcion_misionera = fecha.day // 7 == 2  # Cada tercer sábado del mes es obra misionera
    who = input("Ingrese quién está encargado del programa: ")

    if not who:
        print("Debe ingresar un encargado para el programa.")
        return


    generar_programaex(fecha, titulo_programa, who, opcion_misionera)

import datetime
import random

def existente_programa():
    print("Programa de culto joven")
    fecha_input = input("Ingrese la fecha del programa (YYYY-MM-DD): ")
    try:
        fecha = datetime.datetime.strptime(fecha_input, "%Y-%m-%d").date()
    except ValueError:
        print("Formato de fecha incorrecto. Intente nuevamente.")
        return

    if verificar_fecha_programa(fecha):
        print("Ya existe un programa para esta fecha.")
        return

    titulo_programa = input("Ingrese el título del programa: ")
    opcion_misionera = fecha.day // 7 == 2  # Cada tercer sábado del mes es obra misionera

    if opcion_misionera:
        print("Este programa será de obra misionera.")

    # Crear un diccionario para los participantes
    parti = {}

    who = input("Encargado: ")

    parti["Ejercicio de canto"] = input("Ejercicio de canto: ")
    parti["Dirigir"] = input("Dirigir: ")
    parti["Dinámica"] = input("Dinámica: ")
    parti["Bando de oración"] = input("Bando de oración: ")
    parti["Matutina"] = input("Matutina: ")
    parti["Reflexión"] = input("Reflexión: ")

    hora_inicio = input("Ingrese la hora de inicio del programa (HH:MM): ")

    gen_pro_listo(fecha, titulo_programa, who, parti, hora_inicio, opcion_misionera)


def gen_pro_listo(fecha, titulo_programa, who, parti, hora_inicio, es_misionera=False):
    nombre_archivo = f"aa_{titulo_programa}_{fecha}.txt"
    with open(nombre_archivo, 'w') as archivo:
        archivo.write(f"{titulo_programa} - {fecha}\n".center(50))
        archivo.write("="*50 + "\n")

        if es_misionera:
            archivo.write("Este sábado se realizará obra misionera.\n")
            archivo.write("Los participantes deben estar preparados para actividades.\n")
            print(f"Programa misionero guardado en {nombre_archivo}")
            return

        archivo.write(f"El encargado es: {who}\n")

        try:
            hora_actual = datetime.datetime.strptime(hora_inicio, "%H:%M")
        except ValueError:
            print("Formato de hora incorrecto.")
            return

        # Lista de actividades y sus duraciones
        programa = [
            ("Ejercicio de Canto", 15),
            ("Dirigir", 5),
            ("Dinámica", 20),
            ("Bando de Oración", 10),
            ("Matutina", 20),
            ("Ejercicio Bíblico", 20),
            ("Reflexión", random.randint(15, 20)),
        ]

        for actividad, duracion in programa:
            participante = parti.get(actividad, "Sin asignar")
            hora_fin = hora_actual + datetime.timedelta(minutes=duracion)
            archivo.write(f"{hora_actual.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')} - {actividad} - {participante}\n")
            hora_actual = hora_fin

        print(f"Programa guardado en {nombre_archivo}")








def generar_programaex(fecha, programa_titulo, who, es_misionero=False):
    nombre_archivo = f"aa_{who}_{fecha}.txt"
    with open(nombre_archivo, 'w') as archivo:
        archivo.write(f"{programa_titulo} - {fecha}\n".center(50))
        archivo.write("="*50 + "\n")

        if es_misionero:
            archivo.write("Este sábado se realizará obra misionera.\n")
            archivo.write("Participantes deben estar preparados para actividades\n")
            print(f"Programa misionero guardado en {nombre_archivo}")
            return

        archivo.write(f"El encargado es: {who}\n")
        

    print(f"Programa guardado en {nombre_archivo}")
        



# Función para generar un culto
def generar_culto():
    fecha_input = input("Ingrese la fecha del programa (YYYY-MM-DD): ")
    try:
        fecha = datetime.datetime.strptime(fecha_input, "%Y-%m-%d").date()
    except ValueError:
        print("Formato de fecha incorrecto. Intente nuevamente.")
        return

    if verificar_fecha_programa(fecha):
        print("Ya existe un programa para esta fecha.")
        return

    titulo_programa = input("Ingrese el título del programa: ")
    opcion_misionera = fecha.day // 7 == 2  # Cada tercer sábado del mes es obra misionera

    if opcion_misionera:
        print("Este programa será de obra misionera.")

    # Llamar a la función de asignación de participantes
    participantes = asignar_participantes()
    if not participantes:
        print("No se pudieron asignar todos los participantes.")
        return

    hora_inicio = input("Ingrese la hora de inicio del programa (HH:MM): ")
    generar_programa(fecha, titulo_programa, participantes, hora_inicio, opcion_misionera)

def imprimir_calendario_completo_en_filas():
    try:
        # Solicitar el año al usuario
        year = int(input("Ingrese el año para el calendario: "))
    except ValueError:
        print("Por favor ingrese un año válido.")
        return

    print(f"\nCalendario del año {year}")
    print("=" * 70)
    
    # Crear el calendario de cada mes y agruparlos en filas de 3 meses
    for fila in range(0, 12, 3):
        # Imprimir encabezado con los nombres de los meses
        encabezado = ""
        for mes in range(3):
            encabezado += f"{calendar.month_name[fila + mes + 1]:^20}"
        print(encabezado)

        # Imprimir encabezado de días
        dias = " L  M  M  J  V  S  D   " * 3
        print(dias)

        # Generar las semanas para los tres meses
        semanas_meses = [calendar.monthcalendar(year, fila + mes + 1) for mes in range(3)]

        # Determinar el número máximo de semanas entre los tres meses
        max_semanas = max(len(semana) for semana in semanas_meses)

        # Imprimir las semanas
        for semana in range(max_semanas):
            linea = ""
            for mes in range(3):
                # Verificar si el mes tiene la semana actual
                if semana < len(semanas_meses[mes]):
                    semana_actual = semanas_meses[mes][semana]
                    # Formatear los días de la semana
                    linea += " ".join(f"{dia:2}" if dia != 0 else "  " for dia in semana_actual)
                else:
                    # Si el mes no tiene esta semana, añadir espacios vacíos
                    linea += " " * 20
                linea += "   "  # Separación entre meses
            print(linea)
        print("=" * 70)


# Menú principal
def menu():
    while True:
        print("\n--- Menú Principal ---")
        print("1. Generar un culto")
        print("2. Editar un programa")
        print("3. Ver sábados libres")
        print("4. Agregar nombres a una lista")
        print("5. Agregar progama a las fechas")
        print("6. Agregar programa existente")
        print("7. Ver calendario")
        print("8. Salir")

        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            generar_culto()
        elif opcion == '2':
            editar_programa()
        elif opcion == '3':
            mes = int(input("Ingrese el mes (número): "))
            año = int(input("Ingrese el año: "))
            sabados_libres = obtener_sabados_libres(mes, año)
            print("Sábados libres:", sabados_libres)
        elif opcion == '4':
            print("\n--- Seleccione la lista para agregar nombres ---")
            print("1. Reflexión")
            print("2. Canto")
            print("3. Restantes")
            print("4. Programas")

            lista_opcion = input("Seleccione una opción: ")
            if lista_opcion == '1':
                agregar_nombres(nombres_reflexion, "nombres_reflexion.txt")
            elif lista_opcion == '2':
                agregar_nombres(nombres_canto, "nombres_canto.txt")
            elif lista_opcion == '3':
                agregar_nombres(nombres_restantes, "nombres_restantes.txt")
            elif lista_opcion == '4':
                agregar_nombres(nombres_programas, "nombres_programas.txt")
            else:
                print("Opción de lista no válida.")
        elif opcion == '5':
                existente_fecha()
        elif opcion == '6':
                existente_programa()
        elif opcion == '7':
            imprimir_calendario_completo_en_filas()
        elif opcion == '8':
            break
        else:
            print("Opción no válida.")

menu()

