# Gestor de biblioteca inteligente

Proyecto de gestión de una biblioteca (UI con rich + menú clásico). Incluye:

- Modelos: Libro, Usuario, Prestamo, Biblioteca, GrafoLibros, Cola de solicitudes.
- Persistencia en JSON (carpeta `data/`) a través de `src.persistencia`.
- Interfaz visual con `rich` en `interfaz/` y menú clásico.
- Tests unitarios con `pytest` en `tests/`.

Requisitos

- Python 3.8+ (se desarrolló con Python 3.11)

Instalación y entorno (Windows PowerShell)

1. Crear y activar virtualenv (si no existe):

   python -m venv .venv; .\.venv\Scripts\Activate.ps1

2. Instalar dependencias:

   python -m pip install --upgrade pip; python -m pip install -r requirements.txt

Ejecución

- Ejecutar la interfaz rica (si `rich` funciona):

  python main.py

  `main.py` intenta iniciar la UI rica y cae al menú clásico si hay problema.

Pruebas

- Ejecutar tests con pytest:

  python -m pytest -q

Notas

- Los datos se guardan en la carpeta `data/` en el directorio del proyecto. Los archivos son:
  - `libros.json`, `usuarios.json`, `prestamos.json`, `solicitudes.json`, `grafo.json`.

- Si tienes problemas instalando `rich` por errores de certificado TLS, puedes usar temporalmente `--trusted-host` en pip (ver logs previos en la sesión):

  python -m pip install rich --trusted-host pypi.org --trusted-host files.pythonhosted.org

Contribuir

- Añade más tests en `tests/`.
- Mejorar sincronización entre UIs para grafo y datos.
