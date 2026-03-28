# controllers/producto_controller.py
from models import Producto
from typing import List, Optional

class ProductoController:
    """Controlador para manejar operaciones con productos."""

    def listar_productos(self) -> List[Producto]:
        """Retorna todos los productos activos."""
        return Producto.listar_activos()

    def buscar_productos(self, termino: str) -> List[Producto]:
        """Busca productos por nombre o código."""
        if not termino or len(termino) < 2:
            return self.listar_productos()
        return Producto.buscar(termino)

    def obtener_producto(self, producto_id: int) -> Optional[Producto]:
        """Obtiene un producto por su ID."""
        return Producto.obtener_por_id(producto_id)

    def obtener_producto_por_codigo(self, codigo: str) -> Optional[Producto]:
        """Obtiene un producto por su código."""
        return Producto.obtener_por_codigo(codigo)

    def crear_producto(self, codigo: str, nombre: str, descripcion: str,
                       precio: float, stock: int) -> tuple[bool, str]:
        """
        Crea un nuevo producto.
        Retorna (éxito, mensaje)
        """
        # Validaciones
        if not codigo or not nombre:
            return False, "Código y nombre son obligatorios"

        if precio <= 0:
            return False, "El precio debe ser mayor a 0"

        if stock < 0:
            return False, "El stock no puede ser negativo"

        # Verificar si el código ya existe
        existente = self.obtener_producto_por_codigo(codigo)
        if existente:
            return False, f"Ya existe un producto con el código {codigo}"

        try:
            producto = Producto(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                precio_venta=precio,
                stock=stock
            )
            producto.guardar()
            return True, f"Producto '{nombre}' creado exitosamente"
        except Exception as e:
            return False, f"Error al crear producto: {str(e)}"

    def actualizar_producto(self, producto_id: int, **campos) -> tuple[bool, str]:
        """
        Actualiza un producto existente.
        campos puede incluir: codigo, nombre, descripcion, precio_venta, stock, activo
        """
        producto = self.obtener_producto(producto_id)
        if not producto:
            return False, "Producto no encontrado"

        # Actualizar solo los campos proporcionados
        for key, value in campos.items():
            if hasattr(producto, key):
                setattr(producto, key, value)

        try:
            producto.guardar()
            return True, "Producto actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar producto: {str(e)}"

    def eliminar_producto(self, producto_id: int, borrado_fisico=False) -> tuple[bool, str]:
        """Elimina un producto."""
        producto = self.obtener_producto(producto_id)
        if not producto:
            return False, "Producto no encontrado"

        try:
            producto.eliminar(borrado_fisico)
            tipo_borrado = "eliminado" if borrado_fisico else "desactivado"
            return True, f"Producto {tipo_borrado} exitosamente"
        except Exception as e:
            return False, f"Error al eliminar producto: {str(e)}"