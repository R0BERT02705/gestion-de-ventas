# views/login_view.py
import customtkinter as ctk
from controllers.auth_controller import AuthController
from utils.session import Session

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="white")
        self.parent = parent
        self.on_login_success = on_login_success
        self.auth_controller = AuthController()
        self.session = Session()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de login"""
        # Frame central para el formulario
        self.center_frame = ctk.CTkFrame(
            self, 
            width=800, 
            height=600,
            fg_color="white",
            border_width=1,
            border_color="#e0e0e0",
            corner_radius=10
        )
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title = ctk.CTkLabel(
            self.center_frame,
            text="SISTEMA DE VENTAS",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1a73e8"
        )
        title.pack(pady=(40, 10))
        
        subtitle = ctk.CTkLabel(
            self.center_frame,
            text="Iniciar Sesión",
            font=ctk.CTkFont(size=16),
            text_color="#666666"
        )
        subtitle.pack(pady=(0, 30))
        
        # Campos de entrada
        self.entry_usuario = ctk.CTkEntry(
            self.center_frame,
            width=280,
            height=40,
            placeholder_text="Usuario",
            font=ctk.CTkFont(size=14),
            border_color="#cccccc",
            fg_color="white"
        )
        self.entry_usuario.pack(pady=10)
        
        self.entry_password = ctk.CTkEntry(
            self.center_frame,
            width=280,
            height=40,
            placeholder_text="Contraseña",
            show="•",
            font=ctk.CTkFont(size=14),
            border_color="#cccccc",
            fg_color="white"
        )
        self.entry_password.pack(pady=10)
        self.entry_password.bind("<Return>", lambda e: self.iniciar_sesion())
        
        # Botón de login (azul)
        self.btn_login = ctk.CTkButton(
            self.center_frame,
            text="INICIAR SESIÓN",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1a73e8",
            hover_color="#1557b0",
            command=self.iniciar_sesion
        )
        self.btn_login.pack(pady=20)
        
        # Label para mensajes de error
        self.lbl_mensaje = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        self.lbl_mensaje.pack()
        
    def iniciar_sesion(self):
        """Procesa el intento de login"""
        username = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        
        exito, mensaje, usuario = self.auth_controller.iniciar_sesion(username, password)
        
        if exito:
            self.lbl_mensaje.configure(text="", text_color="green")
            self.on_login_success(usuario)
        else:
            self.lbl_mensaje.configure(text=mensaje, text_color="red")
            self.entry_password.delete(0, "end")