# utils/session.py
class Session:
    """Clase singleton para manejar la sesión del usuario actual."""
    _instance = None
    _usuario_actual = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
        return cls._instance

    @property
    def usuario(self):
        return self._usuario_actual

    @usuario.setter
    def usuario(self, value):
        self._usuario_actual = value

    def limpiar(self):
        self._usuario_actual = None

    def es_admin(self):
        return self._usuario_actual and self._usuario_actual.rol == 'admin'