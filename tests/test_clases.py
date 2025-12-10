import os
from src.clases import Biblioteca, Libro, Usuario, ColaSolicitudes, SolicitudPrestamo
from src import persistencia


def test_quicksort_order():
    b = Biblioteca()
    b.libros = [
        Libro("Zeta", "A", "F", 2000),
        Libro("Alpha", "B", "G", 1999),
        Libro("Beta", "C", "H", 2001),
    ]
    b.ordenar_por_titulo()
    titles = [l.titulo for l in b.libros]
    assert titles == ["Alpha", "Beta", "Zeta"]


def test_cola_procesar():
    usuario = Usuario("Juan", "u1")
    libro = Libro("Mi Libro", "Autor", "Genero", 2020, disponible=True)
    b = Biblioteca()
    b.libros = [libro]
    cola = ColaSolicitudes()
    s = SolicitudPrestamo("u1", "Mi Libro")
    cola.encolar(s)
    prestamos = []
    procesados = cola.procesar([usuario], b, prestamos)
    assert len(procesados) == 1
    assert prestamos[0].libro.titulo == "Mi Libro"
    assert not libro.disponible


def test_persistencia_roundtrip(tmp_path, monkeypatch):
    # usar tmp_path como data dir temporal
    monkeypatch.setattr(persistencia, "DATA_DIR", str(tmp_path))
    l1 = Libro("A", "X", "G", 2000)
    l2 = Libro("B", "Y", "G", 2001)
    persistencia.guardar_datos("libros.json", [l1, l2])
    loaded = persistencia.cargar_libros()
    assert len(loaded) == 2
    assert {x.titulo for x in loaded} == {"A", "B"}
