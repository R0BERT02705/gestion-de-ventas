# views/productos_view.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.producto_controller import ProductoController
from utils.session import Session

class ProductosView(ctk.CTkFrame):
    def __init__(self, parent, usuario):
        super().__init__(parent, fg_color="white")
        self.parent = parent
        self.usuario = usuario
        self.producto_controller = ProductoController()
        self.session = Session()
        
        self.setup_ui()
        self.cargar_productos()
        
    def setup_ui(self):
        """Configura la interfaz de productos"""
        # Frame superior (búsqueda y botones)
        top_frame = ctk.CTkFrame(self, fg_color="white")
        top_frame.pack(fill="x", pady=(0, 10))
        
        # Buscador
        search_frame = ctk.CTkFrame(top_frame, fg_color="white")
        search_frame.pack(side="left", fill="x", expand=True)
        
        self.entry_buscar = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar producto por nombre o código...",
            width=300,
            height=35,
            border_color="#cccccc",
            fg_color="white"
        )
        self.entry_buscar.pack(side="left", padx=(0, 5))
        self.entry_buscar.bind("<KeyRelease>", self.buscar_productos)
        
        btn_buscar = ctk.CTkButton(
            search_frame,
            text="Buscar",
            width=80,
            height=35,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            command=self.buscar_productos
        )
        btn_buscar.pack(side="left")
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(top_frame, fg_color="white")
        btn_frame.pack(side="right")
        
        btn_nuevo = ctk.CTkButton(
            btn_frame,
            text="Nuevo Producto",
            width=120,
            height=35,
            fg_color="#28a745",
            hover_color="#218838",
            command=lambda: self.mostrar_formulario_producto()
        )
        btn_nuevo.pack(side="left", padx=2)
        
        # Frame principal para la tabla
        table_frame = ctk.CTkFrame(self, fg_color="white")
        table_frame.pack(fill="both", expand=True)
        
        # Treeview para productos
        columns = ("Código", "Nombre", "Descripción", "Precio", "Stock", "Estado")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            height=20
        )
        self.tree.heading("#0", text="ID")
        self.tree.heading("Código", text="Código")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Estado", text="Estado")
        
        # Configurar columnas
        self.tree.column("#0", width=50, minwidth=50)
        self.tree.column("Código", width=100, minwidth=80)
        self.tree.column("Nombre", width=200, minwidth=150)
        self.tree.column("Descripción", width=250, minwidth=150)
        self.tree.column("Precio", width=80, minwidth=70)
        self.tree.column("Stock", width=60, minwidth=50)
        self.tree.column("Estado", width=80, minwidth=70)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind doble clic para editar
        self.tree.bind("<Double-Button-1>", self.editar_producto)
        
        # Frame inferior (botones de acción)
        bottom_frame = ctk.CTkFrame(self, fg_color="white")
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        btn_editar = ctk.CTkButton(
            bottom_frame,
            text="Editar",
            width=100,
            height=35,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            command=self.editar_producto_seleccionado
        )
        btn_editar.pack(side="left", padx=2)
        
        btn_eliminar = ctk.CTkButton(
            bottom_frame,
            text="Eliminar",
            width=100,
            height=35,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self.eliminar_producto_seleccionado
        )
        btn_eliminar.pack(side="left", padx=2)
        
        btn_actualizar = ctk.CTkButton(
            bottom_frame,
            text="Actualizar",
            width=100,
            height=35,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            command=self.cargar_productos
        )
        btn_actualizar.pack(side="left", padx=2)
        
        # Deshabilitar botones si no es admin
        if not self.session.es_admin():
            btn_nuevo.configure(state="disabled")
            btn_eliminar.configure(state="disabled")
        
    def cargar_productos(self):
        """Carga todos los productos en la tabla"""
        try:
            productos = self.producto_controller.listar_productos()
            self.actualizar_tabla(productos)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")
        
    def buscar_productos(self, event=None):
        """Busca productos por término"""
        try:
            termino = self.entry_buscar.get()
            productos = self.producto_controller.buscar_productos(termino)
            self.actualizar_tabla(productos)
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar productos: {str(e)}")
        
    def actualizar_tabla(self, productos):
        """Actualiza la tabla con la lista de productos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar productos
        for prod in productos:
            estado = "Activo" if prod.activo else "Inactivo"
            descripcion = (prod.descripcion[:50] + "...") if prod.descripcion and len(prod.descripcion) > 50 else (prod.descripcion or "")
            self.tree.insert(
                "",
                "end",
                text=prod.id,
                values=(
                    prod.codigo,
                    prod.nombre,
                    descripcion,
                    f"${prod.precio_venta:.2f}",
                    prod.stock,
                    estado
                ),
                tags=("activo" if prod.activo else "inactivo",)
            )
        
        # Configurar colores
        self.tree.tag_configure("activo", background="white")
        self.tree.tag_configure("inactivo", background="#ffe6e6")
        
    def mostrar_formulario_producto(self, producto=None):
        """Muestra el formulario para crear/editar producto"""
        # 1. Obtener la ventana principal
        ventana_principal = self.winfo_toplevel()
        
        # 2. Crear diálogo
        dialog = ctk.CTkToplevel(ventana_principal)
        dialog.title("Nuevo Producto" if not producto else "Editar Producto")
        dialog.geometry("500x650")
        
        # 3. Configuración de Modalidad (CORREGIDO)
        dialog.transient(ventana_principal) # Asociar a la ventana principal
        dialog.withdraw() # Ocultar momentáneamente para evitar parpadeo al centrar
        
        # 4. Centrar diálogo
        dialog.update_idletasks()
        x = ventana_principal.winfo_x() + (ventana_principal.winfo_width() // 2) - (500 // 2)
        y = ventana_principal.winfo_y() + (ventana_principal.winfo_height() // 2) - (650 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # 5. Hacer visible y capturar el foco (CORREGIDO)
        dialog.deiconify() # Mostrar ventana
        dialog.wait_visibility() # ESPERAR a que el SO la renderice
        dialog.grab_set() # Ahora sí podemos bloquear el resto de la app
        dialog.focus_set()
        
        # Configurar para que se cierre con Escape
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
        # --- Interfaz del Formulario ---
        title = ctk.CTkLabel(
            dialog,
            text="✨ Nuevo Producto" if not producto else "✏️ Editar Producto",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1a73e8"
        )
        title.pack(pady=20)
        
        form_frame = ctk.CTkFrame(dialog, fg_color="white")
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Campo Código
        ctk.CTkLabel(form_frame, text="Código:", anchor="w", font=ctk.CTkFont(size=13)).pack(fill="x", pady=(10, 2))
        entry_codigo = ctk.CTkEntry(form_frame, height=38, fg_color="white", border_color="#cccccc")
        entry_codigo.pack(fill="x", pady=(0, 10))
        
        # Campo Nombre
        ctk.CTkLabel(form_frame, text="Nombre:", anchor="w", font=ctk.CTkFont(size=13)).pack(fill="x", pady=(10, 2))
        entry_nombre = ctk.CTkEntry(form_frame, height=38, fg_color="white", border_color="#cccccc")
        entry_nombre.pack(fill="x", pady=(0, 10))
        
        # Campo Descripción
        ctk.CTkLabel(form_frame, text="Descripción:", anchor="w", font=ctk.CTkFont(size=13)).pack(fill="x", pady=(10, 2))
        entry_descripcion = ctk.CTkTextbox(form_frame, height=100, fg_color="white", border_width=1, border_color="#cccccc")
        entry_descripcion.pack(fill="x", pady=(0, 10))
        
        # Campo Precio
        ctk.CTkLabel(form_frame, text="Precio de Venta:", anchor="w", font=ctk.CTkFont(size=13)).pack(fill="x", pady=(10, 2))
        entry_precio = ctk.CTkEntry(form_frame, height=38, fg_color="white", border_color="#cccccc")
        entry_precio.pack(fill="x", pady=(0, 10))
        
        # Campo Stock
        ctk.CTkLabel(form_frame, text="Stock:", anchor="w", font=ctk.CTkFont(size=13)).pack(fill="x", pady=(10, 2))
        entry_stock = ctk.CTkEntry(form_frame, height=38, fg_color="white", border_color="#cccccc")
        entry_stock.pack(fill="x", pady=(0, 10))
        
        # Checkbox Activo
        var_activo = ctk.BooleanVar(value=True)
        if producto:
            chk_activo = ctk.CTkCheckBox(form_frame, text="Producto Activo", variable=var_activo, fg_color="#1a73e8")
            chk_activo.pack(pady=10)
        
        # Cargar datos si es edición
        if producto:
            entry_codigo.insert(0, producto.codigo or "")
            entry_nombre.insert(0, producto.nombre or "")
            if producto.descripcion:
                entry_descripcion.insert("1.0", producto.descripcion)
            entry_precio.insert(0, str(producto.precio_venta or "0"))
            entry_stock.insert(0, str(producto.stock or "0"))
            var_activo.set(producto.activo == 1)
        
        # Botones de Acción
        btn_frame = ctk.CTkFrame(dialog, fg_color="white")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        def guardar():
            codigo = entry_codigo.get().strip()
            nombre = entry_nombre.get().strip()
            descripcion = entry_descripcion.get("1.0", "end-1c").strip()
            
            try:
                precio = float(entry_precio.get() or "0")
                stock = int(entry_stock.get() or "0")
            except ValueError:
                messagebox.showerror("Error", "Precio o Stock inválidos", parent=dialog)
                return
            
            if not codigo or not nombre:
                messagebox.showerror("Error", "Código y nombre son obligatorios", parent=dialog)
                return
            
            btn_guardar.configure(state="disabled", text="Guardando...")
            
            try:
                if producto:
                    exito, msg = self.producto_controller.actualizar_producto(
                        producto.id, codigo=codigo, nombre=nombre, descripcion=descripcion,
                        precio_venta=precio, stock=stock, activo=1 if var_activo.get() else 0
                    )
                else:
                    exito, msg = self.producto_controller.crear_producto(codigo, nombre, descripcion, precio, stock)
                
                if exito:
                    messagebox.showinfo("Éxito", msg, parent=dialog)
                    dialog.destroy()
                    self.cargar_productos()
                else:
                    messagebox.showerror("Error", msg, parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {str(e)}", parent=dialog)
            finally:
                btn_guardar.configure(state="normal", text="Guardar")
        
        btn_guardar = ctk.CTkButton(btn_frame, text="Guardar", fg_color="#28a745", command=guardar)
        btn_guardar.pack(side="left", padx=10, expand=True)
        
        btn_cancelar = ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#dc3545", command=dialog.destroy)
        btn_cancelar.pack(side="left", padx=10, expand=True)
        
        dialog.lift()
    def editar_producto(self, event):
        """Edita el producto seleccionado (doble clic)"""
        self.editar_producto_seleccionado()
        
    def editar_producto_seleccionado(self):
        """Edita el producto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = self.tree.item(seleccion[0])
        producto_id = int(item['text'])
        producto = self.producto_controller.obtener_producto(producto_id)
        
        if producto:
            self.mostrar_formulario_producto(producto)
        
    def eliminar_producto_seleccionado(self):
        """Elimina el producto seleccionado"""
        if not self.session.es_admin():
            messagebox.showerror("Error", "Solo administradores pueden eliminar productos")
            return
            
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = self.tree.item(seleccion[0])
        producto_id = int(item['text'])
        producto_nombre = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto '{producto_nombre}'?"):
            exito, msg = self.producto_controller.eliminar_producto(producto_id, borrado_fisico=False)
            if exito:
                messagebox.showinfo("Éxito", msg)
                self.cargar_productos()
            else:
                messagebox.showerror("Error", msg)