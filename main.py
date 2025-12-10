"""Punto de entrada: intenta iniciar la interfaz rica (interfaz.interfaz.main).
Si ocurre algún problema (por ejemplo falta de dependencia), cae al menú clásico
implementado en `interfaz.menu.mostrar_menu()`.
"""

import sys

def main():
    try:
        # Intentar arrancar la interfaz basada en rich
        from interfaz.interfaz import main as rich_main
        rich_main()
        return
    except Exception as e:
        # Mostrar por qué no se pudo arrancar la interfaz rica y usar fallback
        print("No se pudo iniciar la interfaz 'rich'. Se usará el menú clásico.", file=sys.stderr)
        print(f"Detalles: {e}", file=sys.stderr)

    # Fallback al menú de texto
    from interfaz.menu import mostrar_menu
    mostrar_menu()


if __name__ == "__main__":
    main()
