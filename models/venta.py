# models/venta.py
from database.conexion import Database
from models.usuario import Usuario
from models.producto import Producto
from datetime import datetime

class DetalleVenta:
    """Modelo que representa una línea de detalle de venta."""

    def __init__(self, id=None, venta_id=None, producto=None, cantidad=0,
                 precio_unitario=0.0, subtotal=0.0):
        self.id = id
        self.venta_id = venta_id
        self.producto = producto  # Objeto Producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal

    @classmethod
    def from_row(cls, row):
        """Crea una instancia de DetalleVenta a partir de una fila de la BD."""
        if not row:
            return None
        producto = Producto.obtener_por_id(row['producto_id'])
        return cls(
            id=row['id'],
            venta_id=row['venta_id'],
            producto=producto,
            cantidad=row['cantidad'],
            precio_unitario=row['precio_unitario'],
            subtotal=row['subtotal']
        )

    def calcular_subtotal(self):
        """Calcula el subtotal basado en cantidad y precio unitario."""
        self.subtotal = self.cantidad * self.precio_unitario
        return self.subtotal


class Venta:
    """Modelo que representa una venta completa con sus detalles."""

    def __init__(self, id=None, folio=None, usuario=None, fecha=None,
                 total=0.0, detalles=None):
        self.id = id
        self.folio = folio
        self.usuario = usuario  # Objeto Usuario
        self.fecha = fecha or datetime.now()
        self.total = total
        self.detalles = detalles or []  # Lista de objetos DetalleVenta

    @classmethod
    def from_row(cls, row):
        """Crea una instancia de Venta a partir de una fila de la BD."""
        if not row:
            return None
        usuario = Usuario.obtener_por_id(row['usuario_id'])
        return cls(
            id=row['id'],
            folio=row['folio'],
            usuario=usuario,
            fecha=row['fecha'],
            total=row['total']
        )

    @classmethod
    def obtener_por_id(cls, venta_id):
        """Obtiene una venta por su ID, incluyendo sus detalles."""
        db = Database()
        # Obtener cabecera
        query = "SELECT * FROM ventas WHERE id = ?"
        row = db.fetch_one(query, (venta_id,))

        if not row:
            return None

        venta = cls.from_row(row)

        # Obtener detalles
        query = "SELECT * FROM detalle_venta WHERE venta_id = ?"
        detalles_rows = db.fetch_all(query, (venta_id,))
        venta.detalles = [DetalleVenta.from_row(r) for r in detalles_rows]

        return venta

    @classmethod
    def obtener_por_folio(cls, folio):
        """Obtiene una venta por su folio."""
        db = Database()
        query = "SELECT * FROM ventas WHERE folio = ?"
        row = db.fetch_one(query, (folio,))
        return cls.from_row(row) if row else None

    @classmethod
    def listar_por_fecha(cls, fecha_inicio, fecha_fin):
        """
        Lista ventas en un rango de fechas.
        Fechas en formato 'YYYY-MM-DD'
        """
        db = Database()
        query = """
            SELECT v.*, u.nombre_completo as vendedor
            FROM ventas v
            JOIN usuarios u ON v.usuario_id = u.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            ORDER BY v.fecha DESC
        """
        rows = db.fetch_all(query, (fecha_inicio, fecha_fin))
        ventas = []
        for row in rows:
            venta = cls.from_row(row)
            # Podríamos añadir el nombre del vendedor como atributo extra
            ventas.append(venta)
        return ventas

    @classmethod
    def listar_por_vendedor(cls, usuario_id, limite=50):
        """Lista las últimas ventas de un vendedor específico."""
        db = Database()
        query = """
            SELECT * FROM ventas
            WHERE usuario_id = ?
            ORDER BY fecha DESC
            LIMIT ?
        """
        rows = db.fetch_all(query, (usuario_id, limite))
        return [cls.from_row(row) for row in rows]

    @classmethod
    def obtener_estadisticas(cls, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas de ventas en un período.
        Si no se especifican fechas, usa el mes actual.
        """
        db = Database()

        if not fecha_inicio or not fecha_fin:
            # Por defecto, mes actual
            hoy = datetime.now()
            primer_dia = hoy.replace(day=1).strftime('%Y-%m-%d')
            ultimo_dia = hoy.strftime('%Y-%m-%d')
            fecha_inicio = fecha_inicio or primer_dia
            fecha_fin = fecha_fin or ultimo_dia

        query = """
            SELECT
                COUNT(*) as total_ventas,
                SUM(total) as ingresos_totales,
                AVG(total) as ticket_promedio,
                COUNT(DISTINCT usuario_id) as vendedores_activos
            FROM ventas
            WHERE DATE(fecha) BETWEEN ? AND ?
        """
        stats = db.fetch_one(query, (fecha_inicio, fecha_fin))

        # Top productos vendidos
        query_productos = """
            SELECT
                p.nombre,
                SUM(dv.cantidad) as cantidad_vendida,
                SUM(dv.subtotal) as total_generado
            FROM detalle_venta dv
            JOIN productos p ON dv.producto_id = p.id
            JOIN ventas v ON dv.venta_id = v.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY p.id
            ORDER BY cantidad_vendida DESC
            LIMIT 10
        """
        top_productos = db.fetch_all(query_productos, (fecha_inicio, fecha_fin))

        # Top vendedores
        query_vendedores = """
            SELECT
                u.nombre_completo,
                COUNT(*) as ventas_realizadas,
                SUM(v.total) as monto_total
            FROM ventas v
            JOIN usuarios u ON v.usuario_id = u.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY u.id
            ORDER BY monto_total DESC
            LIMIT 10
        """
        top_vendedores = db.fetch_all(query_vendedores, (fecha_inicio, fecha_fin))

        return {
            'resumen': dict(stats) if stats else {},
            'top_productos': [dict(row) for row in top_productos],
            'top_vendedores': [dict(row) for row in top_vendedores],
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }

    def generar_folio(self):
        """Genera un folio único para la venta."""
        db = Database()
        # Formato: VENTA-YYYYMMDD-XXXX
        fecha_str = datetime.now().strftime('%Y%m%d')
        query = """
            SELECT COUNT(*) as count FROM ventas
            WHERE folio LIKE ?
        """
        result = db.fetch_one(query, (f'VENTA-{fecha_str}-%',))
        count = result['count'] if result else 0
        return f"VENTA-{fecha_str}-{count + 1:04d}"

    def agregar_producto(self, producto, cantidad):
        """
        Agrega un producto al detalle de la venta.
        Verifica stock disponible.
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")

        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {producto.stock}")

        # Verificar si el producto ya está en el detalle
        for detalle in self.detalles:
            if detalle.producto.id == producto.id:
                # Actualizar cantidad
                nueva_cantidad = detalle.cantidad + cantidad
                if nueva_cantidad > producto.stock:
                    raise ValueError(f"Stock insuficiente. Disponible: {producto.stock}")
                detalle.cantidad = nueva_cantidad
                detalle.calcular_subtotal()
                self._recalcular_total()
                return

        # Agregar nuevo detalle
        detalle = DetalleVenta(
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio_venta
        )
        detalle.calcular_subtotal()
        self.detalles.append(detalle)
        self._recalcular_total()

    def quitar_producto(self, producto_id):
        """Elimina un producto del detalle de la venta."""
        self.detalles = [d for d in self.detalles if d.producto.id != producto_id]
        self._recalcular_total()

    def _recalcular_total(self):
        """Recalcula el total de la venta basado en los detalles."""
        self.total = sum(detalle.subtotal for detalle in self.detalles)

    def guardar(self):
        """
        Guarda la venta completa en la base de datos.
        Esto incluye:
        1. Insertar la cabecera de venta
        2. Insertar cada detalle
        3. Actualizar el stock de los productos
        """
        if not self.usuario:
            raise ValueError("La venta debe tener un vendedor asignado")

        if not self.detalles:
            raise ValueError("No hay productos en la venta")

        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            # Iniciar transacción
            conn.execute("BEGIN TRANSACTION")

            # Generar folio si no tiene
            if not self.folio:
                self.folio = self.generar_folio()

            # Insertar cabecera
            query_venta = """
                INSERT INTO ventas (folio, usuario_id, total)
                VALUES (?, ?, ?)
            """
            cursor.execute(query_venta, (self.folio, self.usuario.id, self.total))
            self.id = cursor.lastrowid

            # Insertar detalles y actualizar stock
            for detalle in self.detalles:
                # Insertar detalle
                query_detalle = """
                    INSERT INTO detalle_venta
                    (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(query_detalle, (
                    self.id,
                    detalle.producto.id,
                    detalle.cantidad,
                    detalle.precio_unitario,
                    detalle.subtotal
                ))

                # Actualizar stock del producto
                query_stock = """
                    UPDATE productos
                    SET stock = stock - ?
                    WHERE id = ? AND stock >= ?
                """
                cursor.execute(query_stock, (detalle.cantidad, detalle.producto.id, detalle.cantidad))

                # Verificar que se actualizó el stock
                if cursor.rowcount == 0:
                    raise ValueError(f"Stock insuficiente para {detalle.producto.nombre}")

            # Confirmar transacción
            conn.commit()
            return True

        except Exception as e:
            # Revertir cambios en caso de error
            conn.rollback()
            print(f"Error al guardar venta: {e}")
            raise e

    def anular(self):
        """
        Anula una venta (borrado lógico o devolución).
        Esto debería incrementar el stock nuevamente.
        """
        # Por ahora, implementaremos esto después
        # Requiere añadir un campo 'estado' en ventas
        pass

    def __str__(self):
        return f"Venta #{self.folio} - {self.fecha} - Total: ${self.total:.2f}"