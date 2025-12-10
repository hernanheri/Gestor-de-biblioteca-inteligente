from src.clases import Libro, Usuario, Prestamo, Biblioteca, GrafoLibros
from src import persistencia
from src.clases import SolicitudPrestamo, ColaSolicitudes

# Instancias principales del sistema
biblioteca = Biblioteca()
# Cargar datos persistentes (si existen)
biblioteca.libros = persistencia.cargar_libros()
usuarios = persistencia.cargar_usuarios()
prestamos = persistencia.cargar_prestamos(biblioteca.libros, usuarios)
# Cargar solicitudes (cola FIFO)
solicitudes_data = persistencia.cargar_solicitudes()
cola = ColaSolicitudes.from_dict_list(solicitudes_data) if solicitudes_data else ColaSolicitudes()

# Intentar cargar grafo persistido (grafo.json). Si no existe, crear grafo vacío y
# agregar nodos para los libros cargados.
grafo = GrafoLibros()
# construir grafo automáticamente a partir de la biblioteca (conexiones por autor/género)
grafo.build_from_biblioteca(biblioteca)
# persistir el grafo reconstruido (asegura consistencia)
persistencia.guardar_grafo("grafo.json", grafo.to_dict())

# Al iniciar, intentar procesar la cola (por si hay libros disponibles ahora)
procesados_inicio = cola.procesar(usuarios, biblioteca, prestamos)
if procesados_inicio:
    # Guardar cambios si se procesaron solicitudes
    persistencia.guardar_datos("prestamos.json", prestamos)
    persistencia.guardar_datos("libros.json", biblioteca.libros)
    persistencia.guardar_datos("solicitudes.json", cola.to_list())


# ---------------------------------------------------------
#   FUNCIONES DE LA LÓGICA
# ---------------------------------------------------------

def registrar_libro():
    print("\n--- Registrar Libro ---")
    titulo = input("Título: ")
    autor = input("Autor: ")
    genero = input("Género: ")
    try:
        year = int(input("Año: "))
    except Exception:
        year = None

    libro = Libro(titulo, autor, genero, year)
    biblioteca.agregar_libro(libro)
    grafo.agregar_libro(libro)

    # Persistir cambio
    persistencia.guardar_datos("libros.json", biblioteca.libros)
    # Persistir grafo actualizado
    persistencia.guardar_grafo("grafo.json", grafo.to_dict())

    print("\nLibro registrado correctamente.")


def registrar_usuario():
    print("\n--- Registrar Usuario ---")
    nombre = input("Nombre: ")
    id_usuario = input("ID del usuario: ")
    tipo = input("Tipo (estudiante/profesor): ")
    usuario = Usuario(nombre, id_usuario, tipo)
    usuarios.append(usuario)

    # Persistir usuarios
    persistencia.guardar_datos("usuarios.json", usuarios)

    print("\nUsuario registrado correctamente.")


def prestar_libro():
    print("\n--- Prestar Libro ---")
    id_usuario = input("ID del usuario: ")
    titulo = input("Título del libro a prestar: ")

    usuario = next((u for u in usuarios if u.id == id_usuario), None)
    libro = next((l for l in biblioteca.libros if titulo.lower() in l.titulo.lower()), None)

    if not usuario:
        print("Usuario no encontrado.")
        return
    if not libro:
        print("Libro no encontrado.")
        return

    if libro.disponible:
        # Prestar inmediatamente
        libro.disponible = False
        prestamo = Prestamo(usuario, libro)
        prestamos.append(prestamo)
        # Persistir cambios
        persistencia.guardar_datos("prestamos.json", prestamos)
        persistencia.guardar_datos("libros.json", biblioteca.libros)
        print("\nPréstamo realizado con éxito.")
    else:
        # Encolar la solicitud (FIFO)
        s = SolicitudPrestamo(usuario.id, libro.titulo)
        # registrar tipo de usuario para prioridad
        s.tipo_usuario = usuario.tipo
        cola.encolar(s)
        persistencia.guardar_datos("solicitudes.json", cola.to_list())
        print(f"\nEl libro no está disponible. Tu solicitud fue encolada (posición {len(cola.solicitudes)}).")


def devolver_libro():
    print("\n--- Devolver Libro ---")
    titulo = input("Título del libro a devolver: ")

    prestamo = next((p for p in prestamos if p.libro.titulo.lower() == titulo.lower() and p.fecha_devolucion is None), None)

    if not prestamo:
        print("No se encontró un préstamo activo para ese libro.")
        return

    prestamo.devolver()
    # Persistir cambios
    persistencia.guardar_datos("prestamos.json", prestamos)
    persistencia.guardar_datos("libros.json", biblioteca.libros)

    # Intentar procesar la cola de solicitudes después de la devolución
    procesados = cola.procesar(usuarios, biblioteca, prestamos)
    if procesados:
        persistencia.guardar_datos("prestamos.json", prestamos)
        persistencia.guardar_datos("libros.json", biblioteca.libros)
        persistencia.guardar_datos("solicitudes.json", cola.to_list())
        print(f"\nSe procesaron {len(procesados)} solicitudes en la cola.")

    print("\nLibro devuelto correctamente.")


def buscar_libros():
    print("\n--- Buscar Libros ---")
    print("1. Por título")
    print("2. Por autor")
    print("3. Por género")
    print("4. Por año")
    print("5. Disponible")
    opcion = input("\nElige una opción: ")

    if opcion == "1":
        q = input("Título: ")
        resultados = biblioteca.buscar_por_titulo(q)

    elif opcion == "2":
        q = input("Autor: ")
        resultados = biblioteca.buscar_por_autor(q)

    elif opcion == "3":
        q = input("Género: ")
        resultados = biblioteca.buscar_por_genero(q)

    elif opcion == "4":
        q = int(input("Año: "))
        resultados = biblioteca.buscar_por_año(q)

    elif opcion == "5":
        resultados = biblioteca.buscar_disponibles()

    else:
        print("Opción no válida.")
        return

    if resultados:
        print("\nResultados:")
        for libro in resultados:
            print(f"- {libro}")
    else:
        print("No se encontraron coincidencias.")


def relacionar_libros():
    print("\n--- Relacionar Libros (Grafo) ---")
    t1 = input("Título del primer libro: ")
    t2 = input("Título del segundo libro: ")

    libro1 = next((l for l in biblioteca.libros if l.titulo.lower() == t1.lower()), None)
    libro2 = next((l for l in biblioteca.libros if l.titulo.lower() == t2.lower()), None)

    if not libro1 or not libro2:
        print("Uno de los libros no existe.")
        return

    grafo.relacionar(libro1, libro2)
    # Persistir grafo
    persistencia.guardar_grafo("grafo.json", grafo.to_dict())
    print("\nLibros relacionados correctamente.")


def ver_recomendaciones():
    print("\n--- Recomendaciones de Libros (Grafo) ---")
    titulo = input("Título del libro base: ")

    libro = next((l for l in biblioteca.libros if l.titulo.lower() == titulo.lower()), None)
    if not libro:
        print("Libro no encontrado.")
        return

    recomendaciones = grafo.recomendaciones(libro)

    if recomendaciones:
        print("\nLibros relacionados:")
        for r in recomendaciones:
            print("- " + r)
    else:
        print("Este libro no tiene recomendaciones relacionadas.")


def actualizar_libro_menu():
    print("\n--- Actualizar Libro ---")
    titulo = input("Título exacto del libro a actualizar: ")
    libro = next((l for l in biblioteca.libros if l.titulo.lower() == titulo.lower()), None)
    if not libro:
        print("Libro no encontrado.")
        return
    print(f"Libro actual: {libro}")
    nuevo_titulo = input("Nuevo título (ENTER para mantener): ").strip()
    nuevo_autor = input("Nuevo autor (ENTER para mantener): ").strip()
    nuevo_genero = input("Nuevo género (ENTER para mantener): ").strip()
    nuevo_year = input("Nuevo año (ENTER para mantener): ").strip()

    cambios = {}
    if nuevo_titulo:
        cambios['titulo'] = nuevo_titulo
    if nuevo_autor:
        cambios['autor'] = nuevo_autor
    if nuevo_genero:
        cambios['genero'] = nuevo_genero
    if nuevo_year:
        try:
            cambios['year'] = int(nuevo_year)
        except Exception:
            cambios['year'] = None

    if cambios:
        biblioteca.actualizar_libro(titulo, **cambios)
        persistencia.guardar_datos("libros.json", biblioteca.libros)
        print("Libro actualizado.")
    else:
        print("No se hicieron cambios.")


def eliminar_libro_menu():
    print("\n--- Eliminar Libro ---")
    titulo = input("Título exacto del libro a eliminar: ")
    # Buscar objeto Libro para eliminar y actualizar grafo
    libro = next((l for l in biblioteca.libros if l.titulo.lower() == titulo.lower()), None)
    if not libro:
        print("No se encontró el libro.")
        return
    # Remover del grafo
    grafo.remover_libro(libro)
    # Remover de la biblioteca
    ok = biblioteca.eliminar_libro(titulo)
    if ok:
        persistencia.guardar_datos("libros.json", biblioteca.libros)
        persistencia.guardar_grafo("grafo.json", grafo.to_dict())
        print("Libro eliminado.")
    else:
        print("No se pudo eliminar el libro.")


def listar_usuarios():
    print("\n--- Usuarios Registrados ---")
    if not usuarios:
        print("No hay usuarios registrados.")
        return
    for u in usuarios:
        print(f"- {u}")


def actualizar_usuario_menu():
    print("\n--- Actualizar Usuario ---")
    id_u = input("ID del usuario a actualizar: ")
    u = next((x for x in usuarios if x.id == id_u), None)
    if not u:
        print("Usuario no encontrado.")
        return
    nuevo_nombre = input("Nuevo nombre (ENTER para mantener): ").strip()
    nuevo_tipo = input("Nuevo tipo (estudiante/profesor) (ENTER para mantener): ").strip()
    if nuevo_nombre:
        u.nombre = nuevo_nombre
    if nuevo_tipo:
        u.tipo = nuevo_tipo
    persistencia.guardar_datos("usuarios.json", usuarios)
    print("Usuario actualizado.")


def eliminar_usuario_menu():
    print("\n--- Eliminar Usuario ---")
    id_u = input("ID del usuario a eliminar: ")
    idx = next((i for i, x in enumerate(usuarios) if x.id == id_u), None)
    if idx is None:
        print("Usuario no encontrado.")
        return
    del usuarios[idx]
    persistencia.guardar_datos("usuarios.json", usuarios)
    print("Usuario eliminado.")



# ---------------------------------------------------------
#   MENÚ PRINCIPAL
# ---------------------------------------------------------

def mostrar_menu():
    while True:
        print("\n=========== SISTEMA DE BIBLIOTECA ===========")
        print("1. Registrar libro")
        print("2. Registrar usuario")
        print("3. Prestar libro")
        print("4. Devolver libro")
        print("5. Buscar libros")
        print("6. Relacionar libros (grafos)")
        print("7. Ver recomendaciones")
        print("8. Actualizar libro")
        print("9. Eliminar libro")
        print("10. Listar usuarios")
        print("11. Actualizar usuario")
        print("12. Eliminar usuario")
        print("0. Salir")


        opcion = input("\nElige una opción: ")

        if opcion == "1":
            registrar_libro()
        elif opcion == "2":
            registrar_usuario()
        elif opcion == "3":
            prestar_libro()
        elif opcion == "4":
            devolver_libro()
        elif opcion == "5":
            buscar_libros()
        elif opcion == "6":
            relacionar_libros()
        elif opcion == "7":
            ver_recomendaciones()
        elif opcion == "8":
            actualizar_libro_menu()
        elif opcion == "9":
            eliminar_libro_menu()
        elif opcion == "10":
            listar_usuarios()
        elif opcion == "11":
            actualizar_usuario_menu()
        elif opcion == "12":
            eliminar_usuario_menu()
        elif opcion == "0":
            print("\nSaliendo del sistema...")
            break
        else:
            print("Opción no válida.")


# Solo se ejecuta si este archivo es el principal
if __name__ == "__main__":
    mostrar_menu()
