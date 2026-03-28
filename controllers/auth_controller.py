# controllers/auth_controller.py
from models import Usuario
from utils.session import Session

class AuthController:
    """Controlador para manejar la autenticación."""

    def __init__(self):
        self.session = Session()

    def iniciar_sesion(self, username, password):
        """
        Intenta autenticar al usuario.
        Retorna (éxito, mensaje, usuario)
        """
        if not username or not password:
            return False, "Por favor ingrese usuario y contraseña", None

        usuario = Usuario.autenticar(username, password)

        if usuario:
            self.session.usuario = usuario
            return True, f"¡Bienvenido {usuario.nombre_completo}!", usuario
        else:
            return False, "Usuario o contraseña incorrectos", None

    def cerrar_sesion(self):
        """Cierra la sesión actual."""
        self.session.limpiar()

    def obtener_usuario_actual(self):
        """Retorna el usuario logueado."""
        return self.session.usuario