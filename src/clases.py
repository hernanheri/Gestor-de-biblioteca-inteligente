import json
from datetime import datetime

class Libro:
    def __init__(self, titulo: str, autor: str, genero: str, year: int, disponible: bool = True):
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        # Usar atributo 'year' (sin caracteres especiales)
        self.year = year
        self.disponible = disponible

    def __str__(self):
        return f"{self.titulo} - {self.autor} ({self.year}) - {'Disponible' if self.disponible else 'Prestado'}"

    def to_dict(self):
        """Convierte el objeto Libro a diccionario para JSON."""
        # Exportar la clave estándar 'year' y 'genero'/'categoria' para compatibilidad visual.
        return {
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero,
            "categoria": self.genero,
            "year": self.year,
            "disponible": self.disponible
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Libro desde un diccionario."""
        # Aceptar diferentes claves al cargar: 'year' (preferido), o legacy 'año'/'anio'.
        titulo = data.get("titulo")
        autor = data.get("autor")
        genero = data.get("genero", data.get("categoria", ""))
        year = data.get("year", data.get("año", data.get("anio", None)))
        disponible = data.get("disponible", True)

        # Intentar convertir year a int cuando sea posible
        try:
            year = int(year) if year is not None and year != "" else None
        except Exception:
            year = None

        return cls(
            titulo=titulo,
            autor=autor,
            genero=genero,
            year=year,
            disponible=disponible
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
            prestamo.fecha_devolucion = data.get("fecha_devolucion")
            libro.disponible = not bool(prestamo.fecha_devolucion)  # Si hay devolución, disponible=True
            return prestamo
        return None



# -----------------------------------------------------------
#   CLASE PARA MANEJO DE LIBROS Y BÚSQUEDAS
# -----------------------------------------------------------

class Biblioteca:
    def __init__(self):
        self.libros = []  # Lista de objetos Libro
        
    # ---------- ORDENAMIENTO (quicksort por título) ----------
    def _quicksort(self, arr, low, high):
        if low < high:
            p = self._partition(arr, low, high)
            self._quicksort(arr, low, p - 1)
            self._quicksort(arr, p + 1, high)

    def _partition(self, arr, low, high):
        pivot = arr[high].titulo.lower()
        i = low - 1
        for j in range(low, high):
            if arr[j].titulo.lower() <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i+1], arr[high] = arr[high], arr[i+1]
        return i + 1

    def ordenar_por_titulo(self):
        """Ordena self.libros alfabéticamente por título usando quicksort in-place."""
        if not self.libros:
            return
        self._quicksort(self.libros, 0, len(self.libros) - 1)

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

    def buscar_por_año(self, year: int):
        """Devuelve libros del año indicado (parámetro 'year')."""
        return [libro for libro in self.libros if libro.year == year]

    def buscar_disponibles(self):
        """Devuelve solo libros disponibles para préstamo."""
        return [libro for libro in self.libros if libro.disponible]

    def agregar_libro(self, libro: Libro):
        """Añade un libro a la colección."""
        self.libros.append(libro)
        # Reordenar inmediatamente usando quicksort por título
        self.ordenar_por_titulo()

    def actualizar_libro(self, titulo_buscar: str, **kwargs):
        """Actualiza atributos de un libro encontrado por título (parcial o exacto).
        kwargs puede incluir 'titulo','autor','genero','year','disponible'.
        Devuelve True si se actualizó, False si no se encontró."""
        libro = next((l for l in self.libros if l.titulo.lower() == titulo_buscar.lower()), None)
        if not libro:
            return False
        for k, v in kwargs.items():
            if hasattr(libro, k):
                setattr(libro, k, v)
        # Si se cambió el título, reordenar
        self.ordenar_por_titulo()
        return True

    def eliminar_libro(self, titulo_buscar: str):
        """Elimina un libro por título (exacto). Devuelve True si se eliminó."""
        idx = next((i for i, l in enumerate(self.libros) if l.titulo.lower() == titulo_buscar.lower()), None)
        if idx is None:
            return False
        del self.libros[idx]
        return True



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
        """Devuelve una lista de títulos recomendados para un libro.
        Por defecto, realiza una búsqueda en profundidad (DFS) desde el nodo y
        devuelve los títulos alcanzables (excluyendo el libro original).
        """
        # usar DFS para obtener recomendaciones ordenadas por recorrido
        return self.dfs(libro.titulo)

    def remover_libro(self, libro: Libro):
        """Elimina un nodo del grafo y todas las referencias a él."""
        t = libro.titulo
        if t in self.adyacencia:
            # eliminar referencias desde otros nodos
            for otro in list(self.adyacencia.keys()):
                if t in self.adyacencia.get(otro, []):
                    try:
                        self.adyacencia[otro].remove(t)
                    except ValueError:
                        pass
            # eliminar el nodo
            del self.adyacencia[t]

    def to_dict(self):
        """Serializa el grafo a un diccionario simple (JSON-serializable)."""
        return self.adyacencia

    @classmethod
    def from_dict(cls, data: dict):
        g = cls()
        # asegurarse de que las claves y valores son listas
        for k, v in data.items():
            g.adyacencia[k] = list(v) if v is not None else []
        return g

    def build_from_biblioteca(self, biblioteca: 'Biblioteca'):
        """Reconstruye el grafo conectando libros que comparten autor o género.
        Nodo = título del libro. Aristas no dirigidas entre libros con mismo autor o género.
        """
        self.adyacencia = {}
        # agregar nodos
        for l in biblioteca.libros:
            self.adyacencia[l.titulo] = []
        # crear aristas entre pares que compartan autor o género
        n = len(biblioteca.libros)
        for i in range(n):
            for j in range(i+1, n):
                a = biblioteca.libros[i]
                b = biblioteca.libros[j]
                if (a.autor and b.autor and a.autor.lower() == b.autor.lower()) or (a.genero and b.genero and a.genero.lower() == b.genero.lower()):
                    # añadir bidireccional
                    if b.titulo not in self.adyacencia[a.titulo]:
                        self.adyacencia[a.titulo].append(b.titulo)
                    if a.titulo not in self.adyacencia[b.titulo]:
                        self.adyacencia[b.titulo].append(a.titulo)

    def dfs(self, start_title: str, max_depth: int = None):
        """Realiza DFS en el grafo desde start_title.
        Devuelve lista de títulos alcanzables (excluyendo start_title) en orden de visita.
        Si start_title no existe devuelve lista vacía.
        """
        if start_title not in self.adyacencia:
            return []
        visited = set()
        result = []

        def _dfs(node, depth):
            if node in visited:
                return
            visited.add(node)
            if node != start_title:
                result.append(node)
            if max_depth is not None and depth >= max_depth:
                return
            for neigh in self.adyacencia.get(node, []):
                if neigh not in visited:
                    _dfs(neigh, depth+1)

        _dfs(start_title, 0)
        return result


# -----------------------------------------------------------
#   COLA DE SOLICITUDES (FIFO) PARA PRÉSTAMOS
# -----------------------------------------------------------
class SolicitudPrestamo:
    def __init__(self, id_usuario: str, titulo_libro: str, fecha_solicitud: str = None):
        self.id_usuario = id_usuario
        self.titulo_libro = titulo_libro
        self.fecha_solicitud = fecha_solicitud if fecha_solicitud else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # tipo_usuario / prioridad puede añadirse al crear la solicitud
        self.tipo_usuario = None

    def to_dict(self):
        data = {
            "id_usuario": self.id_usuario,
            "titulo_libro": self.titulo_libro,
            "fecha_solicitud": self.fecha_solicitud
        }
        if self.tipo_usuario is not None:
            data["tipo_usuario"] = self.tipo_usuario
        return data

    @classmethod
    def from_dict(cls, data: dict):
        s = cls(
            id_usuario=data.get("id_usuario"),
            titulo_libro=data.get("titulo_libro"),
            fecha_solicitud=data.get("fecha_solicitud")
        )
        # compatibilidad: aceptar tipo_usuario si está presente
        s.tipo_usuario = data.get("tipo_usuario", data.get("tipo", None))
        return s


class ColaSolicitudes:
    def __init__(self):
        self.solicitudes = []  # lista de SolicitudPrestamo

    def encolar(self, solicitud: SolicitudPrestamo):
        # permitir que solicitud tenga tipo_usuario establecido por el caller
        self.solicitudes.append(solicitud)

    def desencolar(self):
        if not self.solicitudes:
            return None
        return self.solicitudes.pop(0)

    def to_list(self):
        return self.solicitudes

    def to_dict_list(self):
        return [s.to_dict() for s in self.solicitudes]

    @classmethod
    def from_dict_list(cls, datos: list):
        c = cls()
        for d in datos:
            c.solicitudes.append(SolicitudPrestamo.from_dict(d))
        return c

    def procesar(self, usuarios: list, biblioteca: 'Biblioteca', prestamos: list):
        """Procesa la cola FIFO: por cada solicitud en orden, si el libro está disponible crea un Prestamo
        y lo añade a prestamos; si no está disponible la solicitud permanece en la cola.
        Devuelve la lista de prestados creados en esta pasada."""
        # Ahora procesamos por prioridad: se considera 'profesor' con mayor prioridad
        # Mapear solicitudes con prioridad y timestamp para estabilidad
        def prioridad(s: SolicitudPrestamo):
            tipo = (s.tipo_usuario or "").lower()
            if tipo == "profesor" or tipo == "teacher":
                return 0
            # por defecto estudiantes y otros tienen prioridad 1
            return 1

        procesados = []
        nuevas = []

        # Ordenar solicitudes por (prioridad, fecha_solicitud) para procesar en orden deseado
        try:
            sorted_solicitudes = sorted(self.solicitudes, key=lambda s: (prioridad(s), s.fecha_solicitud))
        except Exception:
            # fallback si fecha no comparable
            sorted_solicitudes = list(self.solicitudes)

        for s in sorted_solicitudes:
            usuario = next((u for u in usuarios if u.id == s.id_usuario), None)
            libro = next((l for l in biblioteca.libros if l.titulo.lower() == s.titulo_libro.lower()), None)
            if usuario and libro and libro.disponible:
                p = Prestamo(usuario, libro)
                prestamos.append(p)
                libro.disponible = False
                procesados.append(p)
            else:
                # no pudo procesarse — mantener en la nueva lista (preservando original order)
                nuevas.append(s)

        self.solicitudes = nuevas
        return procesados
