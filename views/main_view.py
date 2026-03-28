# views/main_view.py
import customtkinter as ctk
from utils.session import Session
from views.ventas_view import VentasView
from views.productos_view import ProductosView
from views.usuarios_view import UsuariosView
from views.estadisticas_view import EstadisticasView

class MainView(ctk.CTkFrame):
    def __init__(self, parent, usuario):
        super().__init__(parent, fg_color="white")
        self.parent = parent
        self.usuario = usuario
        self.session = Session()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz principal"""
        # Frame superior con información del usuario
        self.top_frame = ctk.CTkFrame(self, height=60, fg_color="#f8f9fa", corner_radius=0)
        self.top_frame.pack(fill="x", padx=0, pady=0)
        self.top_frame.pack_propagate(False)
        
        # Título
        title = ctk.CTkLabel(
            self.top_frame,
            text="SISTEMA DE VENTAS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1a73e8"
        )
        title.pack(side="left", padx=20)
        
        # Información del usuario
        user_info_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        user_info_frame.pack(side="right", padx=20)
        
        user_label = ctk.CTkLabel(
            user_info_frame,
            text=f"Usuario: {self.usuario.nombre_completo}",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        )
        user_label.pack(side="left", padx=10)
        
        role_label = ctk.CTkLabel(
            user_info_frame,
            text=f"({self.usuario.rol.upper()})",
            font=ctk.CTkFont(size=12),
            text_color="#1a73e8"
        )
        role_label.pack(side="left", padx=5)
        
        # Botón cerrar sesión (rojo)
        btn_logout = ctk.CTkButton(
            user_info_frame,
            text="Cerrar Sesión",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self.cerrar_sesion
        )
        btn_logout.pack(side="left", padx=10)
        
        # Frame para las pestañas
        self.tabview = ctk.CTkTabview(
            self,
            fg_color="white",
            segmented_button_fg_color="#F9F9F9",
            segmented_button_selected_color="#1a73e8",
            segmented_button_selected_hover_color="#1557b0",
            segmented_button_unselected_color="#9FF6FA",
            segmented_button_unselected_hover_color="#797777",
            text_color="black",
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self.tab_ventas = self.tabview.add("VENTAS")
        self.tab_productos = self.tabview.add("PRODUCTOS")
        self.tab_usuarios = self.tabview.add("USUARIOS")
        self.tab_estadisticas = self.tabview.add("ESTADÍSTICAS")
        
        # Configurar contenido de las pestañas
        self.setup_ventas_tab()
        self.setup_productos_tab()
        self.setup_usuarios_tab()
        self.setup_estadisticas_tab()
        
    def setup_ventas_tab(self):
        """Configura la pestaña de ventas"""
        ventas_view = VentasView(self.tab_ventas, self.usuario)
        ventas_view.pack(fill="both", expand=True)
        
    def setup_productos_tab(self):
        """Configura la pestaña de productos"""
        productos_view = ProductosView(self.tab_productos, self.usuario)
        productos_view.pack(fill="both", expand=True)
        
    def setup_usuarios_tab(self):
        """Configura la pestaña de usuarios (solo admin)"""
        usuarios_view = UsuariosView(self.tab_usuarios, self.usuario)
        usuarios_view.pack(fill="both", expand=True)
        
        # Si no es admin, deshabilitar acciones
        if not self.session.es_admin():
            for widget in self.tab_usuarios.winfo_children():
                if isinstance(widget, ctk.CTkButton) and widget.cget("text") not in ["Actualizar", "Cancelar"]:
                    widget.configure(state="disabled")

    def setup_estadisticas_tab(self):
        """Configura la pestaña de estadísticas"""
        estadisticas_view = EstadisticasView(self.tab_estadisticas, self.usuario)
        estadisticas_view.pack(fill="both", expand=True)
        
    def cerrar_sesion(self):
        """Cierra la sesión actual y redirige al Login"""
        self.session.limpiar()
        
        # Intentamos usar la referencia centralizada en MainApplication
        if hasattr(self.parent, 'app_instance'):
            # Esto llama al método show_login() de tu clase MainApplication en main.py
            self.parent.app_instance.show_login()
        else:
            # Fallback de seguridad en caso de que la referencia no exista
            self.destroy()
            from views.login_view import LoginView
            # Intentamos obtener la función de éxito desde el objeto app si es posible
            success_callback = getattr(self.parent, 'on_login_success', None)
            login_view = LoginView(self.parent, success_callback)
            login_view.pack(fill="both", expand=True)