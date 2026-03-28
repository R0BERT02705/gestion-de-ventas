# models/producto.py
from database.conexion import Database

class Producto:
    """Modelo que representa un producto en el inventario."""

    def __init__(self, id=None, codigo=None, nombre=None, descripcion=None,
                 precio_venta=0.0, stock=0, activo=1, fecha_creacion=None):
        self.id = id
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio_venta = precio_venta
        self.stock = stock
        self.activo = activo
        self.fecha_creacion = fecha_creacion

    @classmethod
    def from_row(cls, row):
        """Crea una instancia de Producto a partir de una fila de la BD."""
        if not row:
            return None
        return cls(
            id=row['id'],
            codigo=row['codigo'],
            nombre=row['nombre'],
            descripcion=row['descripcion'],
            precio_venta=row['precio_venta'],
            stock=row['stock'],
            activo=row['activo'],
            fecha_creacion=row['fecha_creacion']
        )

    @classmethod
    def obtener_por_id(cls, producto_id):
        """Obtiene un producto por su ID."""
        db = Database()
        query = "SELECT * FROM productos WHERE id = ?"
        row = db.fetch_one(query, (producto_id,))
        return cls.from_row(row)

    @classmethod
    def obtener_por_codigo(cls, codigo):
        """Obtiene un producto por su código."""
        db = Database()
        query = "SELECT * FROM productos WHERE codigo = ?"
        row = db.fetch_one(query, (codigo,))
        return cls.from_row(row)

    @classmethod
    def buscar(cls, termino):
        """
        Busca productos por nombre o código (búsqueda parcial).
        Retorna productos activos que coincidan.
        """
        db = Database()
        query = """
            SELECT * FROM productos 
            WHERE activo = 1 AND (nombre LIKE ? OR codigo LIKE ?)
            ORDER BY nombre
        """
        params = (f'%{termino}%', f'%{termino}%')
        rows = db.fetch_all(query, params)
        return [cls.from_row(row) for row in rows]

    @classmethod
    def listar_activos(cls):
        """Lista todos los productos activos."""
        db = Database()
        query = "SELECT * FROM productos WHERE activo = 1 ORDER BY nombre"
        rows = db.fetch_all(query)
        return [cls.from_row(row) for row in rows]

    @classmethod
    def listar_con_stock_bajo(cls, limite=5):
        """Lista productos con stock por debajo del límite especificado."""
        db = Database()
        query = """
            SELECT * FROM productos 
            WHERE activo = 1 AND stock <= ? 
            ORDER BY stock
        """
        rows = db.fetch_all(query, (limite,))
        return [cls.from_row(row) for row in rows]

    def guardar(self):
        """Guarda o actualiza el producto en la base de datos."""
        db = Database()
        if self.id:  # Actualizar
            query = """
                UPDATE productos 
                SET codigo = ?, nombre = ?, descripcion = ?, 
                    precio_venta = ?, stock = ?, activo = ?
                WHERE id = ?
            """
            params = (self.codigo, self.nombre, self.descripcion,
                     self.precio_venta, self.stock, self.activo, self.id)
            db.execute_query(query, params)
        else:  # Insertar nuevo
            query = """
                INSERT INTO productos (codigo, nombre, descripcion, precio_venta, stock, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (self.codigo, self.nombre, self.descripcion,
                     self.precio_venta, self.stock, self.activo)
            self.id = db.execute_query(query, params)

    def actualizar_stock(self, cantidad):
        """
        Actualiza el stock del producto.
        cantidad puede ser positiva (aumentar) o negativa (disminuir).
        Retorna True si la operación fue exitosa, False si no hay suficiente stock.
        """
        if self.stock + cantidad < 0:
            return False  # No hay suficiente stock

        db = Database()
        query = "UPDATE productos SET stock = stock + ? WHERE id = ?"
        result = db.execute_query(query, (cantidad, self.id))

        if result is not None:
            self.stock += cantidad
            return True
        return False

    def eliminar(self, borrado_fisico=False):
        """
        Elimina un producto.
        Por defecto hace borrado lógico (desactiva).
        Si borrado_fisico=True, lo elimina permanentemente.
        """
        db = Database()
        if borrado_fisico:
            query = "DELETE FROM productos WHERE id = ?"
        else:
            query = "UPDATE productos SET activo = 0 WHERE id = ?"
        db.execute_query(query, (self.id,))
        if not borrado_fisico:
            self.activo = 0

    def __str__(self):
        return f"{self.codigo} - {self.nombre} (${self.precio_venta:.2f})"