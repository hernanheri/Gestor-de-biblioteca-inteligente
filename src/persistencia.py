import json
import os
from .clases import Libro, Usuario, Prestamo

DATA_DIR = "data"

def guardar_datos(nombre_archivo: str, datos):
    """Guarda una lista de objetos en un archivo JSON."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    ruta = os.path.join(DATA_DIR, nombre_archivo)
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump([d.to_dict() for d in datos], f, indent=2, ensure_ascii=False)


def cargar_libros() -> list:
    """Carga libros desde JSON."""
    ruta = os.path.join(DATA_DIR, "libros.json")
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return [Libro.from_dict(d) for d in datos]
    return []


def cargar_usuarios() -> list:
    """Carga usuarios desde JSON."""
    ruta = os.path.join(DATA_DIR, "usuarios.json")
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return [Usuario.from_dict(d) for d in datos]
    return []


def cargar_prestamos(libros_registrados: list, usuarios_registrados: list) -> list:
    """Carga préstamos desde JSON, reconstruyendo referencias a libros y usuarios."""
    ruta = os.path.join(DATA_DIR, "prestamos.json")
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        prestamos = []
        for d in datos:
            p = Prestamo.from_dict(d, usuarios_registrados, libros_registrados)
            if p:
                prestamos.append(p)
        return prestamos
    return []