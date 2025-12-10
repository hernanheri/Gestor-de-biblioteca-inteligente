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
from src.persistencia import cargar_libros as _persist_cargar_libros, guardar_datos, cargar_grafo, guardar_grafo
from src.clases import Libro

# -----------------------
# Config colores pastel
# -----------------------
ROSA = "#f7cce6"
MORADO = "#d5b8ff"
BLANCO = "white"

# -----------------------
# Rutas y consola
# -----------------------
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LIBROS_FILE = DATA_DIR / "libros.json"

console = Console()


# -----------------------
# Util: delegar persistencia al módulo src.persistencia
# -----------------------
def cargar_libros():
    libros_obj = _persist_cargar_libros()
    return [l.to_dict() for l in libros_obj]


def guardar_libros_from_dicts(libros_dicts):
    objetos = []
    for d in libros_dicts:
        genero = d.get("genero", d.get("categoria", ""))
        try:
            year = int(d.get("year")) if d.get("year") not in (None, "") else None
        except Exception:
            year = None
        objetos.append(Libro(d.get("titulo"), d.get("autor"), genero, year, d.get("disponible", True)))
    guardar_datos("libros.json", objetos)

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
        "Interfaz de diseño (rosa pastel, morado pastel y blanco) — usa los números para navegar.",
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
    opciones.append("1. Ver libros disponibles\n", style=f"bold {ROSA}")
    opciones.append("2. Buscar un libro específico\n", style=f"bold {MORADO}")
    opciones.append("3. Recomendaciones de libros\n", style=f"bold {ROSA}")
    opciones.append("4. Agregar libro\n", style=f"bold {MORADO}")
    opciones.append("5. Salir\n", style=f"bold {ROSA}")

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
    guardar_libros_from_dicts(libros)
    asegurar_grafo_agrega(titulo)
    console.print(Panel(f"[bold green]Libro agregado:[/bold green] {titulo}", border_style="green"))

# -----------------------
# Programa principal
# -----------------------
def main():
    console.clear()
    while True:
        mostrar_encabezado()
        mostrar_menu()
        opcion = Prompt.ask(f"[{MORADO}]Elige una opción[/]", choices=["1","2","3","4","5"], default="1")
        console.clear()

        if opcion == "1":
            mostrar_encabezado()
            ver_libros()
        elif opcion == "2":
            mostrar_encabezado()
            buscar_libro()
        elif opcion == "3":
            mostrar_encabezado()
            recomendaciones()
        elif opcion == "4":
            mostrar_encabezado()
            agregar_libro()
        elif opcion == "5":
            console.print(Panel("[bold magenta]Gracias por usar la biblioteca — ¡éxito con tu tarea! 💗[/bold magenta]", border_style=MORADO))
            break

        # pausar para que el usuario vea resultados
        console.print()
        Prompt.ask(f"[{ROSA}]Presiona ENTER para volver al menú[/]", default="")

if __name__ == "__main__":
    main()