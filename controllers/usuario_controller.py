# controllers/usuario_controller.py
from models import Usuario
from typing import List, Optional

class UsuarioController:
    """Controlador para manejar operaciones con usuarios."""

    def listar_usuarios(self) -> List[Usuario]:
        """Lista todos los usuarios."""
        return Usuario.listar_todos()

    def listar_activos(self) -> List[Usuario]:
        """Lista solo usuarios activos."""
        return Usuario.listar_activos()

    def obtener_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por su ID."""
        return Usuario.obtener_por_id(usuario_id)

    def crear_usuario(self, username: str, password: str, nombre_completo: str,
                      rol: str = 'vendedor') -> tuple[bool, str]:
        """
        Crea un nuevo usuario.
        Retorna (éxito, mensaje)
        """
        # Validaciones
        if not username or not password or not nombre_completo:
            return False, "Todos los campos son obligatorios"

        # Verificar si el usuario ya existe
        # Nota: Habría que implementar un método obtener_por_username
        # Por ahora, esta validación se haría en la BD al guardar

        try:
            usuario = Usuario(
                username=username,
                password=password,
                nombre_completo=nombre_completo,
                rol=rol
            )
            usuario.guardar()
            return True, f"Usuario '{username}' creado exitosamente"
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return False, f"El nombre de usuario '{username}' ya existe"
            return False, f"Error al crear usuario: {str(e)}"

    def actualizar_usuario(self, usuario_id: int, **campos) -> tuple[bool, str]:
        """
        Actualiza un usuario existente.
        campos puede incluir: username, password, nombre_completo, rol, activo
        """
        usuario = self.obtener_usuario(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado"

        # Actualizar campos
        for key, value in campos.items():
            if hasattr(usuario, key):
                setattr(usuario, key, value)

        try:
            usuario.guardar()
            return True, "Usuario actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar usuario: {str(e)}"

    def eliminar_usuario(self, usuario_id: int, borrado_fisico=False) -> tuple[bool, str]:
        """Elimina un usuario."""
        usuario = self.obtener_usuario(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado"

        try:
            usuario.eliminar(borrado_fisico)
            tipo_borrado = "eliminado" if borrado_fisico else "desactivado"
            return True, f"Usuario {tipo_borrado} exitosamente"
        except Exception as e:
            return False, f"Error al eliminar usuario: {str(e)}"