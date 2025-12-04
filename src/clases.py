import json
from datetime import datetime

class Libro:
    def __init__(self, titulo: str, autor: str, genero: str, año: int, disponible: bool = True):
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.año = año
        self.disponible = disponible

    def __str__(self):
        return f"{self.titulo} - {self.autor} ({self.año}) - {'Disponible' if self.disponible else 'Prestado'}"

    def to_dict(self):
        """Convierte el objeto Libro a diccionario para JSON."""
        return {
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero,
            "año": self.año,
            "disponible": self.disponible
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Libro desde un diccionario."""
        return cls(
            titulo=data["titulo"],
            autor=data["autor"],
            genero=data["genero"],
            año=data["año"],
            disponible=data["disponible"]
        )


class Usuario:
    def __init__(self, nombre: str, id_usuario: str, tipo: str = "estudiante"):
        self.nombre = nombre
        self.id = id_usuario
        self.tipo = tipo  # "estudiante" o "profesor" (para prioridad)

    def __str__(self):
        return f"{self.nombre} ({self.id}) - {self.tipo}"

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "id": self.id,
            "tipo": self.tipo
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            nombre=data["nombre"],
            id_usuario=data["id"],
            tipo=data["tipo"]
        )


class Prestamo:
    def __init__(self, usuario: Usuario, libro: Libro, fecha_prestamo: str = None):
        self.usuario = usuario
        self.libro = libro
        self.fecha_prestamo = fecha_prestamo if fecha_prestamo else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_devolucion = None

    def devolver(self):
        """Marca el libro como devuelto."""
        self.fecha_devolucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.libro.disponible = True

    def __str__(self):
        return f"Prestamo: {self.libro.titulo} -> {self.usuario.nombre} ({self.fecha_prestamo})"

    def to_dict(self):
        return {
            "usuario": self.usuario.to_dict(),
            "libro": self.libro.to_dict(),
            "fecha_prestamo": self.fecha_prestamo,
            "fecha_devolucion": self.fecha_devolucion
        }

    @classmethod
    def from_dict(cls, data: dict, usuarios_registrados: list, libros_registrados: list):
        # Buscar usuario y libro por ID/título
        usuario_data = data["usuario"]
        libro_data = data["libro"]

        usuario = next((u for u in usuarios_registrados if u.id == usuario_data["id"]), None)
        libro = next((l for l in libros_registrados if l.titulo == libro_data["titulo"]), None)

        if usuario and libro:
            prestamo = cls(usuario, libro, data["fecha_prestamo"])
            prestamo.fecha_devolucion = data["fecha_devolucion"]
            libro.disponible = not prestamo.fecha_devolucion  # Si hay devolución, disponible=True
            return prestamo
        return None