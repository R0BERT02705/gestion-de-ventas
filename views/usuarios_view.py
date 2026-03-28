# views/usuarios_view.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.usuario_controller import UsuarioController
from utils.session import Session

class UsuariosView(ctk.CTkFrame):
    def __init__(self, parent, usuario):
        super().__init__(parent, fg_color="white")
        self.parent = parent
        self.usuario = usuario # Usuario actual de la sesión
        self.usuario_controller = UsuarioController()
        self.session = Session()
        
        self.setup_ui()
        self.cargar_usuarios()
        
    def setup_ui(self):
        """Configura la interfaz de usuarios"""
        top_frame = ctk.CTkFrame(self, fg_color="white")
        top_frame.pack(fill="x", pady=(0, 10))
        
        search_frame = ctk.CTkFrame(top_frame, fg_color="white")
        search_frame.pack(side="left", fill="x", expand=True)
        
        self.entry_buscar = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar usuario por nombre...",
            width=300,
            height=35,
            border_color="#cccccc",
            fg_color="white"
        )
        self.entry_buscar.pack(side="left", padx=(0, 5))
        self.entry_buscar.bind("<KeyRelease>", self.buscar_usuarios)
        
        # Botones de acción superior
        btn_nuevo = ctk.CTkButton(
            top_frame,
            text="Nuevo Usuario",
            width=120,
            height=35,
            fg_color="#28a745",
            hover_color="#218838",
            command=self.mostrar_formulario_usuario
        )
        btn_nuevo.pack(side="right", padx=2)
        
        # Tabla
        table_frame = ctk.CTkFrame(self, fg_color="white")
        table_frame.pack(fill="both", expand=True)
        
        columns = ("Usuario", "Nombre Completo", "Rol", "Estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Nombre Completo", text="Nombre Completo")
        self.tree.heading("Rol", text="Rol")
        self.tree.heading("Estado", text="Estado")
        
        self.tree.column("Usuario", width=120)
        self.tree.column("Nombre Completo", width=250)
        self.tree.column("Rol", width=100)
        self.tree.column("Estado", width=80)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Botones inferiores
        bottom_frame = ctk.CTkFrame(self, fg_color="white")
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(bottom_frame, text="Editar", command=self.editar_usuario_seleccionado).pack(side="left", padx=2)
        btn_eliminar = ctk.CTkButton(bottom_frame, text="Eliminar", fg_color="#dc3545", command=self.eliminar_usuario_seleccionado)
        btn_eliminar.pack(side="left", padx=2)
        
        if not self.session.es_admin():
            btn_nuevo.configure(state="disabled")
            btn_eliminar.configure(state="disabled")

    def cargar_usuarios(self):
        try:
            usuarios = self.usuario_controller.listar_usuarios()
            self.actualizar_tabla(usuarios)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar: {str(e)}")

    def actualizar_tabla(self, usuarios):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for user in usuarios:
            # Nota: user.id se guarda en los valores internos si prefieres, 
            # aquí lo usaremos como el 'iid' del item para recuperarlo fácil.
            self.tree.insert("", "end", iid=user.id, values=(
                user.username, user.nombre_completo, user.rol, "Activo" if user.activo else "Inactivo"
            ))

    def mostrar_formulario_usuario(self, usuario=None):
        """Muestra ventana modal corregida para CustomTkinter 5.2.2"""
        ventana_principal = self.winfo_toplevel()
        
        # Crear la ventana
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Usuario" if usuario else "Nuevo Usuario")
        dialog.geometry("450x600")
        
        # 1. Configuración inicial de visibilidad
        dialog.withdraw()  # Ocultamos para evitar parpadeo mientras centramos
        dialog.transient(ventana_principal)
        
        # 2. Centrar la ventana
        dialog.update_idletasks()
        x = ventana_principal.winfo_x() + (ventana_principal.winfo_width() // 2) - 225
        y = ventana_principal.winfo_y() + (ventana_principal.winfo_height() // 2) - 300
        dialog.geometry(f"+{x}+{y}")
        
        # 3. Función interna para activar el "grab" de forma segura
        def activar_modal():
            if dialog.winfo_exists():
                dialog.deiconify() # Mostramos la ventana
                dialog.focus_set() # Damos el foco
                dialog.grab_set()  # Ahora no fallará porque la ventana ya es "visible"

        # 4. Lanzar la activación con un pequeño retraso (crucial en CTK 5.2.2)
        dialog.after(200, activar_modal)

        # --- Contenedor de la Interfaz (Igual que antes) ---
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(form_frame, text="Username:").pack(anchor="w")
        entry_user = ctk.CTkEntry(form_frame)
        entry_user.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Nombre Completo:").pack(anchor="w")
        entry_nombre = ctk.CTkEntry(form_frame)
        entry_nombre.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Rol:").pack(anchor="w")
        combo_rol = ctk.CTkComboBox(form_frame, values=["vendedor", "admin"])
        combo_rol.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Password:").pack(anchor="w")
        entry_pass = ctk.CTkEntry(form_frame, show="*")
        entry_pass.pack(fill="x", pady=(0, 10))

        if usuario:
            entry_user.insert(0, usuario.username)
            # Asegúrate que el modelo tenga 'nombre_completo'
            entry_nombre.insert(0, getattr(usuario, 'nombre_completo', ''))
            combo_rol.set(usuario.rol)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)

        def guardar():
            u, n, r, p = entry_user.get(), entry_nombre.get(), combo_rol.get(), entry_pass.get()
            
            if usuario:
                params = {"username": u, "nombre_completo": n, "rol": r}
                if p: params["password"] = p
                exito, msg = self.usuario_controller.actualizar_usuario(usuario.id, **params)
            else:
                exito, msg = self.usuario_controller.crear_usuario(
                    username=u, password=p, nombre_completo=n, rol=r
                )

            if exito:
                messagebox.showinfo("Éxito", msg)
                dialog.destroy()
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(btn_frame, text="Guardar", fg_color="#28a745", command=guardar).pack(side="left", expand=True, padx=10)
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#dc3545", command=dialog.destroy).pack(side="left", expand=True, padx=10)

    def editar_usuario_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return messagebox.showwarning("Aviso", "Seleccione un usuario")
        
        usuario_id = int(seleccion[0])
        usuario = self.usuario_controller.obtener_usuario(usuario_id)
        if usuario:
            self.mostrar_formulario_usuario(usuario)

    def eliminar_usuario_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion: return
        usuario_id = int(seleccion[0])
        
        if usuario_id == self.usuario.id:
            return messagebox.showerror("Error", "No puedes eliminarte a ti mismo")

        if messagebox.askyesno("Confirmar", "¿Desea eliminar este usuario?"):
            exito, msg = self.usuario_controller.eliminar_usuario(usuario_id)
            if exito:
                self.cargar_usuarios()
            messagebox.showinfo("Resultado", msg)

    def buscar_usuarios(self, event=None):
        termino = self.entry_buscar.get().lower()
        todos = self.usuario_controller.listar_usuarios()
        filtrados = [u for u in todos if termino in u.nombre_completo.lower() or termino in u.username.lower()]
        self.actualizar_tabla(filtrados)