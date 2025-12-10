# biblioteca.py
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.align import Align
from pathlib import Path
import json
import random
from src.persistencia import cargar_libros as _persist_cargar_libros, guardar_datos, cargar_grafo, guardar_grafo, cargar_usuarios, cargar_prestamos, cargar_solicitudes
from src.clases import Libro, Usuario, Prestamo, Biblioteca, GrafoLibros, SolicitudPrestamo, ColaSolicitudes

# --------------------------------------------------
# Inicializar datos y estructuras (igual que menú clásico)
# --------------------------------------------------
biblioteca = Biblioteca()
# cargar libros (devuelve objetos Libro)
biblioteca.libros = _persist_cargar_libros()
usuarios = cargar_usuarios()
prestamos = cargar_prestamos(biblioteca.libros, usuarios)

# cola de solicitudes
solicitudes_data = cargar_solicitudes()
cola = ColaSolicitudes.from_dict_list(solicitudes_data) if solicitudes_data else ColaSolicitudes()

# grafo
grafo = GrafoLibros()
# construir grafo automáticamente a partir de la biblioteca (conexiones por autor/género)
grafo.build_from_biblioteca(biblioteca)
# persistir el grafo reconstruido (asegura consistencia)
guardar_grafo("grafo.json", grafo.to_dict())

# procesar cola al inicio
procesados_inicio = cola.procesar(usuarios, biblioteca, prestamos)
if procesados_inicio:
    guardar_datos("prestamos.json", prestamos)
    guardar_datos("libros.json", biblioteca.libros)
    guardar_datos("solicitudes.json", cola.to_list())

# -----------------------
# Config colores pastel
# -----------------------
ROSA = "#f7cce6"
MORADO = "#d5b8ff"
BLANCO = "white"

# -----------------------
# Rutas y consola
# -----------------------
console = Console()


# -----------------------
# Util: delegar persistencia al módulo src.persistencia
# -----------------------
def cargar_libros():
    # devuelve lista de diccionarios para compatibilidad con la UI
    libros_obj = _persist_cargar_libros()
    return [l.to_dict() for l in libros_obj]


def guardar_libros_from_dicts(libros_dicts):
    # convertir dicts a objetos Libro y delegar a guardar_datos
    objetos = []
    for d in libros_dicts:
        genero = d.get("genero", d.get("categoria", ""))
        # intentar convertir year a int si es posible
        try:
            year = int(d.get("year")) if d.get("year") not in (None, "") else None
        except Exception:
            year = None
        objetos.append(Libro(d.get("titulo"), d.get("autor"), genero, year, d.get("disponible", True)))
    # ordenar usando la implementación de quicksort de Biblioteca
    b_temp = Biblioteca()
    b_temp.libros = objetos
    b_temp.ordenar_por_titulo()
    guardar_datos("libros.json", b_temp.libros)

def asegurar_grafo_agrega(titulo):
    g = cargar_grafo("grafo.json") or {}
    if titulo not in g:
        g[titulo] = []
        guardar_grafo("grafo.json", g)

# -----------------------
# UI: Mostrar panel principal
# -----------------------
def mostrar_encabezado():
    titulo = Text("📚  BIBLIOTECA DE LIBROS  🌸", justify="center", style=f"bold {MORADO}")
    descripcion = Text(
        "Gestor de biblioteca inteligente ",
        style="dim"
    )
    header = Panel(
        Align.center(titulo + "\n" + descripcion),
        border_style=MORADO,
        padding=(1, 2),
    )
    console.print(header)

def mostrar_menu():
    opciones = Text()
    opciones.append("1. Usuarios (Registrar / Listar / Actualizar / Eliminar)\n", style=f"bold {ROSA}")
    opciones.append("2. Libros (Submenú de operaciones)\n", style=f"bold {MORADO}")
    opciones.append("3. Ver recomendaciones\n", style=f"bold {ROSA}")
    opciones.append("0. Salir\n", style=f"bold {MORADO}")

    panel = Panel(
        opciones,
        title=Text("🌸 MENÚ", style=f"bold {MORADO}"),
        border_style=MORADO,
        style=f"on {BLANCO}",
        padding=(1, 2),
    )
    console.print(panel)

# -----------------------
# Funcionalidades
# -----------------------
def ver_libros():
    libros = cargar_libros()
    if not libros:
        console.print(Panel("[bold red]No hay libros agregados aún.[/bold red]", border_style="red"))
        return

    tabla = Table(title="📚 Libros disponibles", show_lines=False, border_style=MORADO)
    tabla.add_column("No.", style=f"bold {MORADO}", width=5)
    tabla.add_column("Título", style=f"bold {ROSA}")
    tabla.add_column("Autor", style=f"{MORADO}")
    tabla.add_column("Año", style=f"{ROSA}", justify="center")
    tabla.add_column("Categoría", style=f"{MORADO}")

    for i, libro in enumerate(libros, start=1):
        tabla.add_row(
            str(i),
            libro.get("titulo", "-"),
            libro.get("autor", "-"),
            str(libro.get("year", "-")),
            libro.get("categoria", "-")
        )

    console.print(tabla)


def usuarios_menu():
    while True:
        panel = Panel(Text("1. Registrar usuario\n2. Listar usuarios\n3. Actualizar usuario\n4. Eliminar usuario\n0. Volver"), title=Text("👥 Usuarios", style=f"bold {MORADO}"), border_style=MORADO)
        console.print(panel)
        opt = Prompt.ask(f"[{ROSA}]Elige opción (Usuarios)[/]").strip()
        console.clear()
        o = opt.lower()
        # aceptar '0' o 'v'/'volver'/'b' para volver
        if o in ("0", "v", "b", "volver", "back"):
            break
        if o == "1" or o.startswith("1"):
            registrar_usuario()
        elif o == "2" or o.startswith("2"):
            listar_usuarios()
        elif o == "3" or o.startswith("3"):
            actualizar_usuario_menu()
        elif o == "4" or o.startswith("4"):
            eliminar_usuario_menu()
        console.print()
        Prompt.ask(f"[{ROSA}]Presiona ENTER para continuar[/]", default="")


def libros_menu():
    while True:
        panel = Panel(Text("1. Registrar libro\n2. Ver libros\n3. Buscar libros\n4. Prestar libro\n5. Devolver libro\n6. Relacionar libros\n7. Ver recomendaciones\n8. Actualizar libro\n9. Eliminar libro\n0. Volver"), title=Text("📚 Libros", style=f"bold {MORADO}"), border_style=MORADO)
        console.print(panel)
        opt = Prompt.ask(f"[{ROSA}]Elige opción (Libros)[/]").strip()
        console.clear()
        o = opt.lower()
        if o in ("0", "v", "b", "volver", "back"):
            break
        if o == "1" or o.startswith("1"):
            registrar_libro()
        elif o == "2" or o.startswith("2"):
            ver_libros()
        elif o == "3" or o.startswith("3"):
            buscar_libros()
        elif o == "4" or o.startswith("4"):
            prestar_libro()
        elif o == "5" or o.startswith("5"):
            devolver_libro()
        elif o == "6" or o.startswith("6"):
            relacionar_libros()
        elif o == "7" or o.startswith("7"):
            ver_recomendaciones()
        elif o == "8" or o.startswith("8"):
            actualizar_libro_menu()
        elif o == "9" or o.startswith("9"):
            eliminar_libro_menu()
        console.print()
        Prompt.ask(f"[{ROSA}]Presiona ENTER para continuar[/]", default="")


def registrar_libro():
    console.print(Panel("[bold]➕ Registrar Libro[/bold]", border_style=ROSA))
    titulo = Prompt.ask(f"[{MORADO}]Título[/]").strip()
    if not titulo:
        console.print("[bold red]El título no puede estar vacío.[/bold red]")
        return
    autor = Prompt.ask(f"[{MORADO}]Autor[/]").strip() or "Desconocido"
    genero = Prompt.ask(f"[{MORADO}]Género[/]").strip() or "General"
    year_str = Prompt.ask(f"[{MORADO}]Año[/]").strip()
    try:
        year = int(year_str) if year_str else None
    except Exception:
        year = None

    libro = Libro(titulo, autor, genero, year)
    biblioteca.agregar_libro(libro)
    # reconstruir grafo según autor/género
    grafo.build_from_biblioteca(biblioteca)
    guardar_datos("libros.json", biblioteca.libros)
    guardar_grafo("grafo.json", grafo.to_dict())
    console.print(Panel(f"[bold green]Libro registrado:[/bold green] {titulo}", border_style="green"))


def registrar_usuario():
    console.print(Panel("[bold]➕ Registrar Usuario[/bold]", border_style=ROSA))
    nombre = Prompt.ask(f"[{MORADO}]Nombre[/]").strip()
    id_usuario = Prompt.ask(f"[{MORADO}]ID del usuario[/]").strip()
    tipo = Prompt.ask(f"[{MORADO}]Tipo (estudiante/profesor)[/]").strip() or "estudiante"
    usuario = Usuario(nombre, id_usuario, tipo)
    usuarios.append(usuario)
    guardar_datos("usuarios.json", usuarios)
    console.print(Panel(f"[bold green]Usuario registrado:[/bold green] {nombre}", border_style="green"))


def prestar_libro():
    console.print(Panel("[bold]📦 Prestar Libro[/bold]", border_style=MORADO))
    id_usuario = Prompt.ask(f"[{MORADO}]ID del usuario[/]").strip()
    titulo = Prompt.ask(f"[{MORADO}]Título del libro a prestar[/]").strip()
    usuario = next((u for u in usuarios if u.id == id_usuario), None)
    libro = next((l for l in biblioteca.libros if titulo.lower() in l.titulo.lower()), None)
    if not usuario:
        console.print("[bold red]Usuario no encontrado.[/bold red]")
        return
    if not libro:
        console.print("[bold red]Libro no encontrado.[/bold red]")
        return
    if libro.disponible:
        libro.disponible = False
        prestamo = Prestamo(usuario, libro)
        prestamos.append(prestamo)
        guardar_datos("prestamos.json", prestamos)
        guardar_datos("libros.json", biblioteca.libros)
        console.print(Panel("[bold green]Préstamo realizado con éxito.[/bold green]", border_style="green"))
    else:
        s = SolicitudPrestamo(usuario.id, libro.titulo)
        # registrar tipo de usuario para prioridad
        s.tipo_usuario = usuario.tipo
        cola.encolar(s)
        guardar_datos("solicitudes.json", cola.to_list())
        console.print(Panel(f"[bold yellow]El libro no está disponible. Solicitud encolada (posición {len(cola.solicitudes)})[/bold yellow]", border_style="yellow"))


def devolver_libro():
    console.print(Panel("[bold]↩️ Devolver Libro[/bold]", border_style=ROSA))
    titulo = Prompt.ask(f"[{MORADO}]Título del libro a devolver[/]").strip()
    prestamo = next((p for p in prestamos if p.libro.titulo.lower() == titulo.lower() and p.fecha_devolucion is None), None)
    if not prestamo:
        console.print("[bold red]No se encontró un préstamo activo para ese libro.[/bold red]")
        return
    prestamo.devolver()
    guardar_datos("prestamos.json", prestamos)
    guardar_datos("libros.json", biblioteca.libros)
    procesados = cola.procesar(usuarios, biblioteca, prestamos)
    if procesados:
        guardar_datos("prestamos.json", prestamos)
        guardar_datos("libros.json", biblioteca.libros)
        guardar_datos("solicitudes.json", cola.to_list())
        console.print(Panel(f"[bold green]Se procesaron {len(procesados)} solicitudes en la cola.[/bold green]", border_style="green"))
    console.print(Panel("[bold green]Libro devuelto correctamente.[/bold green]", border_style="green"))


def buscar_libros():
    console.print(Panel("[bold]🔎 Buscar Libros[/bold]", border_style=MORADO))
    opciones = {"1":"Por título","2":"Por autor","3":"Por género","4":"Por año","5":"Disponible"}
    choice = Prompt.ask("Elige: 1-título,2-autor,3-género,4-año,5-disponible", choices=list(opciones.keys()))
    resultados = []
    if choice == "1":
        q = Prompt.ask("Título:").strip()
        resultados = biblioteca.buscar_por_titulo(q)
    elif choice == "2":
        q = Prompt.ask("Autor:").strip()
        resultados = biblioteca.buscar_por_autor(q)
    elif choice == "3":
        q = Prompt.ask("Género:").strip()
        resultados = biblioteca.buscar_por_genero(q)
    elif choice == "4":
        q = Prompt.ask("Año:").strip()
        try:
            qn = int(q)
        except Exception:
            qn = None
        resultados = biblioteca.buscar_por_año(qn)
    elif choice == "5":
        resultados = biblioteca.buscar_disponibles()
    if resultados:
        tabla = Table(title="Resultados", border_style=MORADO)
        tabla.add_column("Título", style=f"bold {ROSA}")
        tabla.add_column("Autor", style=f"{MORADO}")
        tabla.add_column("Año", style=f"{ROSA}")
        tabla.add_column("Estado", style=f"{MORADO}")
        for l in resultados:
            tabla.add_row(l.titulo, l.autor, str(l.year), "Disponible" if l.disponible else "Prestado")
        console.print(tabla)
    else:
        console.print(Panel("[bold red]No se encontraron coincidencias.[/bold red]", border_style="red"))


def relacionar_libros():
    console.print(Panel("[bold]🔗 Relacionar Libros[/bold]", border_style=MORADO))
    t1 = Prompt.ask("Título del primer libro:").strip()
    t2 = Prompt.ask("Título del segundo libro:").strip()
    libro1 = next((l for l in biblioteca.libros if l.titulo.lower() == t1.lower()), None)
    libro2 = next((l for l in biblioteca.libros if l.titulo.lower() == t2.lower()), None)
    if not libro1 or not libro2:
        console.print("[bold red]Uno de los libros no existe.[/bold red]")
        return
    grafo.relacionar(libro1, libro2)
    guardar_grafo("grafo.json", grafo.to_dict())
    console.print(Panel("[bold green]Libros relacionados correctamente.[/bold green]", border_style="green"))


def ver_recomendaciones():
    console.print(Panel("[bold]✨ Recomendaciones (Grafo)[/bold]", border_style=ROSA))
    titulo = Prompt.ask("Título del libro base:").strip()
    libro = next((l for l in biblioteca.libros if l.titulo.lower() == titulo.lower()), None)
    if not libro:
        console.print("[bold red]Libro no encontrado.[/bold red]")
        return
    recomendaciones = grafo.recomendaciones(libro)
    if recomendaciones:
        for r in recomendaciones:
            console.print(f"- {r}")
    else:
        console.print(Panel("[bold yellow]Este libro no tiene recomendaciones relacionadas.[/bold yellow]", border_style="yellow"))


def actualizar_libro_menu():
    console.print(Panel("[bold]✏️ Actualizar Libro[/bold]", border_style=MORADO))
    titulo = Prompt.ask("Título exacto del libro a actualizar:").strip()
    libro = next((l for l in biblioteca.libros if l.titulo.lower() == titulo.lower()), None)
    if not libro:
        console.print("[bold red]Libro no encontrado.[/bold red]")
        return
    nuevo_titulo = Prompt.ask("Nuevo título (ENTER para mantener):", default="").strip()
    nuevo_autor = Prompt.ask("Nuevo autor (ENTER para mantener):", default="").strip()
    nuevo_genero = Prompt.ask("Nuevo género (ENTER para mantener):", default="").strip()
    nuevo_year = Prompt.ask("Nuevo año (ENTER para mantener):", default="").strip()
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
        # reconstruir grafo porque título/autor/género pueden haber cambiado
        guardar_datos("libros.json", biblioteca.libros)
        grafo.build_from_biblioteca(biblioteca)
        guardar_grafo("grafo.json", grafo.to_dict())
        console.print(Panel("[bold green]Libro actualizado.[/bold green]", border_style="green"))
    else:
        console.print("No se hicieron cambios.")


def eliminar_libro_menu():
    console.print(Panel("[bold]🗑️ Eliminar Libro[/bold]", border_style=ROSA))
    titulo = Prompt.ask("Título exacto del libro a eliminar:").strip()
    libro = next((l for l in biblioteca.libros if l.titulo.lower() == titulo.lower()), None)
    if not libro:
        console.print("[bold red]No se encontró el libro.[/bold red]")
        return
    ok = biblioteca.eliminar_libro(titulo)
    if ok:
        # reconstruir grafo tras eliminación
        grafo.build_from_biblioteca(biblioteca)
        guardar_datos("libros.json", biblioteca.libros)
        guardar_grafo("grafo.json", grafo.to_dict())
        console.print(Panel("[bold green]Libro eliminado.[/bold green]", border_style="green"))
    else:
        console.print("[bold red]No se pudo eliminar el libro.[/bold red]")


def listar_usuarios():
    console.print(Panel("[bold]👥 Usuarios Registrados[/bold]", border_style=MORADO))
    if not usuarios:
        console.print("No hay usuarios registrados.")
        return
    for u in usuarios:
        console.print(f"- {u}")


def actualizar_usuario_menu():
    console.print(Panel("[bold]✏️ Actualizar Usuario[/bold]", border_style=ROSA))
    id_u = Prompt.ask("ID del usuario a actualizar:").strip()
    u = next((x for x in usuarios if x.id == id_u), None)
    if not u:
        console.print("[bold red]Usuario no encontrado.[/bold red]")
        return
    nuevo_nombre = Prompt.ask("Nuevo nombre (ENTER para mantener):", default="").strip()
    nuevo_tipo = Prompt.ask("Nuevo tipo (estudiante/profesor) (ENTER para mantener):", default="").strip()
    if nuevo_nombre:
        u.nombre = nuevo_nombre
    if nuevo_tipo:
        u.tipo = nuevo_tipo
    guardar_datos("usuarios.json", usuarios)
    console.print(Panel("[bold green]Usuario actualizado.[/bold green]", border_style="green"))


def eliminar_usuario_menu():
    console.print(Panel("[bold]🗑️ Eliminar Usuario[/bold]", border_style=MORADO))
    id_u = Prompt.ask("ID del usuario a eliminar:").strip()
    idx = next((i for i, x in enumerate(usuarios) if x.id == id_u), None)
    if idx is None:
        console.print("[bold red]Usuario no encontrado.[/bold red]")
        return
    del usuarios[idx]
    guardar_datos("usuarios.json", usuarios)
    console.print(Panel("[bold green]Usuario eliminado.[/bold green]", border_style="green"))

def buscar_libro():
    termino = Prompt.ask(f"[{MORADO}]🔎 Escribe título o palabra para buscar[/]").strip()
    if not termino:
        console.print("[bold red]No escribiste nada.[/bold red]")
        return

    libros = cargar_libros()
    resultados = [
        libro for libro in libros
        if termino.lower() in libro.get("titulo", "").lower()
    ]

    if not resultados:
        console.print(Panel(f"[bold red]No se encontraron libros para:[/bold red] '{termino}'", border_style="red"))
        return

    tabla = Table(title=f"🔍 Resultados: '{termino}'", border_style=MORADO)
    tabla.add_column("Título", style=f"bold {ROSA}")
    tabla.add_column("Autor", style=f"{MORADO}")
    tabla.add_column("Año", style=f"{ROSA}", justify="center")
    tabla.add_column("Categoría", style=f"{MORADO}")

    for libro in resultados:
        tabla.add_row(
            libro.get("titulo", "-"),
            libro.get("autor", "-"),
            str(libro.get("year", "-")),
            libro.get("categoria", "-")
        )

    console.print(tabla)

def recomendaciones():
    libros = cargar_libros()
    if not libros:
        console.print(Panel("[bold red]No hay libros para recomendar.[/bold red]", border_style="red"))
        return

    cantidad = min(3, len(libros))
    recomendados = random.sample(libros, cantidad)

    tabla = Table(title="✨ Recomendaciones", border_style=MORADO)
    tabla.add_column("Título", style=f"bold {ROSA}")
    tabla.add_column("Autor", style=f"{MORADO}")
    tabla.add_column("Categoría", style=f"{ROSA}")

    for libro in recomendados:
        tabla.add_row(libro.get("titulo", "-"), libro.get("autor", "-"), libro.get("categoria", "-"))

    console.print(tabla)

def agregar_libro():
    console.print(Panel("[bold]➕ Agregar un libro[/bold]", border_style=ROSA))
    titulo = Prompt.ask(f"[{MORADO}]Título[/]").strip()
    if not titulo:
        console.print("[bold red]El título no puede estar vacío.[/bold red]")
        return
    autor = Prompt.ask(f"[{MORADO}]Autor[/]").strip() or "Desconocido"
    year = Prompt.ask(f"[{MORADO}]Año[/]").strip() or ""
    categoria = Prompt.ask(f"[{MORADO}]Categoría[/]").strip() or "General"

    libro_dict = {"titulo": titulo, "autor": autor, "year": year, "categoria": categoria}
    libros = cargar_libros()
    libros.append(libro_dict)
    # guardar usando el adaptador que convierte dicts a objetos Libro
    guardar_libros_from_dicts(libros)
    # recargar biblioteca en memoria y reconstruir grafo según autor/género
    biblioteca.libros = _persist_cargar_libros()
    grafo.build_from_biblioteca(biblioteca)
    guardar_grafo("grafo.json", grafo.to_dict())
    console.print(Panel(f"[bold green]Libro agregado:[/bold green] {titulo}", border_style="green"))

# -----------------------
# Programa principal
# -----------------------
def main():
    console.clear()
    while True:
        mostrar_encabezado()
        mostrar_menu()
        opcion = Prompt.ask(f"[{MORADO}]Elige una opción[/]", choices=["0","1","2","3"], default="1")
        console.clear()

        if opcion == "1":
            mostrar_encabezado()
            usuarios_menu()
        elif opcion == "2":
            mostrar_encabezado()
            libros_menu()
        elif opcion == "3":
            mostrar_encabezado()
            ver_recomendaciones()
        elif opcion == "0":
            console.print(Panel("[bold magenta]Gracias por usar la biblioteca — ¡éxito con tu tarea! 💗[/bold magenta]", border_style=MORADO))
            break

        # pausar para que el usuario vea resultados
        console.print()
        Prompt.ask(f"[{ROSA}]Presiona ENTER para volver al menú[/]", default="")

if __name__ == "__main__":
    main()