# models/usuario.py
from database.conexion import Database

class Usuario:
    """Modelo que representa un vendedor en el sistema."""

    def __init__(self, id=None, username=None, password=None, nombre_completo=None,
                 rol='vendedor', activo=1, fecha_creacion=None):
        self.id = id
        self.username = username
        self.password = password  # En producción debería ir hasheada
        self.nombre_completo = nombre_completo
        self.rol = rol
        self.activo = activo
        self.fecha_creacion = fecha_creacion

    @classmethod
    def from_row(cls, row):
        """Crea una instancia de Usuario a partir de una fila de la BD."""
        if not row:
            return None
        return cls(
            id=row['id'],
            username=row['username'],
            password=row['password'],
            nombre_completo=row['nombre_completo'],
            rol=row['rol'],
            activo=row['activo'],
            fecha_creacion=row['fecha_creacion']
        )

    @classmethod
    def autenticar(cls, username, password):
        """
        Autentica un usuario por username y password.
        Retorna el objeto Usuario si las credenciales son válidas, None en caso contrario.
        """
        db = Database()
        query = "SELECT * FROM usuarios WHERE username = ? AND password = ? AND activo = 1"
        row = db.fetch_one(query, (username, password))

        if row:
            return cls.from_row(row)
        return None

    @classmethod
    def obtener_por_id(cls, usuario_id):
        """Obtiene un usuario por su ID."""
        db = Database()
        query = "SELECT * FROM usuarios WHERE id = ?"
        row = db.fetch_one(query, (usuario_id,))
        return cls.from_row(row)

    @classmethod
    def listar_activos(cls):
        """Lista todos los usuarios activos."""
        db = Database()
        query = "SELECT * FROM usuarios WHERE activo = 1 ORDER BY nombre_completo"
        rows = db.fetch_all(query)
        return [cls.from_row(row) for row in rows]

    @classmethod
    def listar_todos(cls):
        """Lista todos los usuarios (activos e inactivos)."""
        db = Database()
        query = "SELECT * FROM usuarios ORDER BY nombre_completo"
        rows = db.fetch_all(query)
        return [cls.from_row(row) for row in rows]

    def guardar(self):
        """Guarda o actualiza el usuario en la base de datos."""
        db = Database()
        if self.id:  # Actualizar
            query = """
                UPDATE usuarios 
                SET username = ?, password = ?, nombre_completo = ?, 
                    rol = ?, activo = ?
                WHERE id = ?
            """
            params = (self.username, self.password, self.nombre_completo,
                     self.rol, self.activo, self.id)
            db.execute_query(query, params)
        else:  # Insertar nuevo
            query = """
                INSERT INTO usuarios (username, password, nombre_completo, rol, activo)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (self.username, self.password, self.nombre_completo,
                     self.rol, self.activo)
            self.id = db.execute_query(query, params)

    def eliminar(self, borrado_fisico=False):
        """
        Elimina un usuario.
        Por defecto hace borrado lógico (desactiva).
        Si borrado_fisico=True, lo elimina permanentemente.
        """
        db = Database()
        if borrado_fisico:
            query = "DELETE FROM usuarios WHERE id = ?"
        else:
            query = "UPDATE usuarios SET activo = 0 WHERE id = ?"
        db.execute_query(query, (self.id,))
        if not borrado_fisico:
            self.activo = 0

    def __str__(self):
        return f"Usuario: {self.username} - {self.nombre_completo} ({self.rol})"