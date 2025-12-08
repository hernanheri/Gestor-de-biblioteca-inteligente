from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Colores pastel
rosa = "#f7cce6"
morado = "#d5b8ff"
blanco = "white"

def mostrar_menu():
    titulo = Text("🌸  MENÚ DE BIBLIOTECA  💜", justify="center")
    titulo.stylize(f"bold {morado}")

    opciones = Text()
    opciones.append("1. Ver libros disponibles\n", style=f"bold {rosa}")
    opciones.append("2. Buscar un libro específico\n", style=f"bold {morado}")
    opciones.append("3. Recomendaciones de libros\n", style=f"bold {rosa}")
    opciones.append("4. Salir\n", style=f"bold {morado}")

    panel = Panel(
        opciones, 
        title=titulo, 
        border_style=morado,
        style=f"on {blanco}"
    )

    console.print(panel)

def main():
    while True:
        console.clear()
        mostrar_menu()

        opcion = console.input(f"\n💗 Ingresa una opción: ")

        if opcion == "1":
            console.print(f"\n📚 [bold {rosa}]Mostrando libros disponibles...[/]")
            console.input("\nPresiona ENTER para continuar 💞")

        elif opcion == "2":
            console.print(f"\n🔍 [bold {morado}]Buscar un libro...[/]")
            console.input("\nPresiona ENTER para continuar 💞")

        elif opcion == "3":
            console.print(f"\n💡 [bold {rosa}]Recomendaciones de libros...[/]")
            console.input("\nPresiona ENTER para continuar 💞")

        elif opcion == "4":
            console.print(f"\n💜 Gracias por usar la biblioteca, bb 💗")
            break

        else:
            console.print("[bold red]❌ Opción inválida.[/]")
            console.input("\nPresiona ENTER para continuar 💞")

if __name__ == "__main__":
    main()