from src.clases import Libro, Usuario, Prestamo, Biblioteca, GrafoLibros

# Instancias principales del sistema
biblioteca = Biblioteca()
grafo = GrafoLibros()
prestamos = []
usuarios = []


# ---------------------------------------------------------
#   FUNCIONES DE LA LÓGICA
# ---------------------------------------------------------

def registrar_libro():
    print("\n--- Registrar Libro ---")
    titulo = input("Título: ")
    autor = input("Autor: ")
    genero = input("Género: ")
    año = int(input("Año: "))

    libro = Libro(titulo, autor, genero, año)
    biblioteca.agregar_libro(libro)
    grafo.agregar_libro(libro)

    print("\nLibro registrado correctamente.")


def registrar_usuario():
    print("\n--- Registrar Usuario ---")
    nombre = input("Nombre: ")
    id_usuario = input("ID del usuario: ")
    tipo = input("Tipo (estudiante/profesor): ")

    usuario = Usuario(nombre, id_usuario, tipo)
    usuarios.append(usuario)

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
    if not libro.disponible:
        print("El libro está prestado.")
        return

    libro.disponible = False
    prestamo = Prestamo(usuario, libro)
    prestamos.append(prestamo)

    print("\nPréstamo realizado con éxito.")


def devolver_libro():
    print("\n--- Devolver Libro ---")
    titulo = input("Título del libro a devolver: ")

    prestamo = next((p for p in prestamos if p.libro.titulo.lower() == titulo.lower() and p.fecha_devolucion is None), None)

    if not prestamo:
        print("No se encontró un préstamo activo para ese libro.")
        return

    prestamo.devolver()
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
        elif opcion == "0":
            print("\nSaliendo del sistema...")
            break
        else:
            print("Opción no válida.")


# Solo se ejecuta si este archivo es el principal
if __name__ == "__main__":
    mostrar_menu()
