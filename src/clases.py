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



# -----------------------------------------------------------
#   CLASE PARA MANEJO DE LIBROS Y BÚSQUEDAS
# -----------------------------------------------------------

class Biblioteca:
    def __init__(self):
        self.libros = []  # Lista de objetos Libro

    # ---------- MÉTODOS DE BÚSQUEDA ----------
    def buscar_por_titulo(self, titulo: str):
        """Devuelve una lista de libros cuyo título coincide parcial."""
        return [libro for libro in self.libros if titulo.lower() in libro.titulo.lower()]

    def buscar_por_autor(self, autor: str):
        """Devuelve libros que coinciden parcialmente con el autor."""
        return [libro for libro in self.libros if autor.lower() in libro.autor.lower()]

    def buscar_por_genero(self, genero: str):
        """Devuelve libros del género especificado."""
        return [libro for libro in self.libros if genero.lower() in libro.genero.lower()]

    def buscar_por_año(self, año: int):
        """Devuelve libros del año indicado."""
        return [libro for libro in self.libros if libro.año == año]

    def buscar_disponibles(self):
        """Devuelve solo libros disponibles para préstamo."""
        return [libro for libro in self.libros if libro.disponible]

    def agregar_libro(self, libro: Libro):
        """Añade un libro a la colección."""
        self.libros.append(libro)



# -----------------------------------------------------------
#   GRAFO SIMPLE PARA LIBROS RELACIONADOS (RECOMENDACIONES)
# -----------------------------------------------------------

class GrafoLibros:
    def __init__(self):
        self.adyacencia = {}   # {titulo : [titulos relacionados]}

    def agregar_libro(self, libro: Libro):
        """Agrega un nodo al grafo si no existe."""
        if libro.titulo not in self.adyacencia:
            self.adyacencia[libro.titulo] = []

    def relacionar(self, libro1: Libro, libro2: Libro):
        """Crea una relación simple entre dos libros (bidireccional)."""
        t1 = libro1.titulo
        t2 = libro2.titulo

        if t1 not in self.adyacencia:
            self.adyacencia[t1] = []
        if t2 not in self.adyacencia:
            self.adyacencia[t2] = []

        if t2 not in self.adyacencia[t1]:
            self.adyacencia[t1].append(t2)
        if t1 not in self.adyacencia[t2]:
            self.adyacencia[t2].append(t1)

    def recomendaciones(self, libro: Libro):
        """Devuelve una lista de títulos recomendados para un libro."""
        return self.adyacencia.get(libro.titulo, [])
