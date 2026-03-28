# views/ventas_view.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.venta_controller import VentaController
from controllers.producto_controller import ProductoController
from models.producto import Producto
from models.venta import Venta, DetalleVenta
from datetime import datetime

class VentasView(ctk.CTkFrame):
    def __init__(self, parent, usuario):
        super().__init__(parent, fg_color="white")
        self.parent = parent
        self.usuario = usuario
        self.venta_controller = VentaController()
        self.producto_controller = ProductoController()
        
        self.venta_actual = None
        self.carrito_items = []
        
        self.setup_ui()
        self.nueva_venta()
        
    def setup_ui(self):
        """Configura la interfaz de ventas"""
        # Frame izquierdo (productos y carrito)
        left_frame = ctk.CTkFrame(self, width=500, fg_color="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # Frame derecho (estadísticas y ventas recientes)
        right_frame = ctk.CTkFrame(self, width=400, fg_color="white")
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # === SECCIÓN IZQUIERDA ===
        # Buscador de productos
        search_frame = ctk.CTkFrame(left_frame, fg_color="white")
        search_frame.pack(fill="x", pady=(0, 10))
        
        self.entry_buscar = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar producto por código o nombre...",
            height=35,
            border_color="#cccccc",
            fg_color="white"
        )
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_buscar.bind("<KeyRelease>", self.buscar_productos)
        self.entry_buscar.bind("<Return>", self.agregar_por_codigo)
        
        btn_buscar = ctk.CTkButton(
            search_frame,
            text="Buscar",
            width=80,
            height=35,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            command=self.buscar_productos
        )
        btn_buscar.pack(side="right")
        
        # Lista de productos
        productos_label = ctk.CTkLabel(
            left_frame,
            text="Productos Disponibles",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#666666"
        )
        productos_label.pack(anchor="w", pady=(5, 5))
        
        # Treeview para productos
        self.tree_productos = ttk.Treeview(
            left_frame,
            columns=("Código", "Nombre", "Precio", "Stock"),
            show="tree headings",
            height=8
        )
        self.tree_productos.heading("#0", text="ID")
        self.tree_productos.heading("Código", text="Código")
        self.tree_productos.heading("Nombre", text="Nombre")
        self.tree_productos.heading("Precio", text="Precio")
        self.tree_productos.heading("Stock", text="Stock")
        
        self.tree_productos.column("#0", width=50)
        self.tree_productos.column("Código", width=100)
        self.tree_productos.column("Nombre", width=200)
        self.tree_productos.column("Precio", width=80)
        self.tree_productos.column("Stock", width=60)
        
        self.tree_productos.pack(fill="both", expand=True, pady=(0, 10))
        self.tree_productos.bind("<Double-Button-1>", self.agregar_al_carrito)
        
        # Carrito de compras
        carrito_label = ctk.CTkLabel(
            left_frame,
            text="Carrito de Compras",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#666666"
        )
        carrito_label.pack(anchor="w", pady=(5, 5))
        
        # Treeview para carrito
        self.tree_carrito = ttk.Treeview(
            left_frame,
            columns=("Producto", "Cantidad", "P.U.", "Subtotal"),
            show="tree headings",
            height=8
        )
        self.tree_carrito.heading("#0", text="ID")
        self.tree_carrito.heading("Producto", text="Producto")
        self.tree_carrito.heading("Cantidad", text="Cant.")
        self.tree_carrito.heading("P.U.", text="P.Unit.")
        self.tree_carrito.heading("Subtotal", text="Subtotal")
        
        self.tree_carrito.column("#0", width=50)
        self.tree_carrito.column("Producto", width=200)
        self.tree_carrito.column("Cantidad", width=60)
        self.tree_carrito.column("P.U.", width=80)
        self.tree_carrito.column("Subtotal", width=100)
        
        self.tree_carrito.pack(fill="both", expand=True, pady=(0, 10))
        self.tree_carrito.bind("<Delete>", self.quitar_del_carrito)
        
        # Total y botones
        total_frame = ctk.CTkFrame(left_frame, fg_color="white")
        total_frame.pack(fill="x", pady=(5, 0))
        
        self.lbl_total = ctk.CTkLabel(
            total_frame,
            text="Total: $0.00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1a73e8"
        )
        self.lbl_total.pack(side="left")
        
        btn_frame = ctk.CTkFrame(total_frame, fg_color="white")
        btn_frame.pack(side="right")
        
        btn_nueva = ctk.CTkButton(
            btn_frame,
            text="Nueva Venta",
            width=100,
            height=35,
            fg_color="#28a745",  # Verde
            hover_color="#218838",
            command=self.nueva_venta
        )
        btn_nueva.pack(side="left", padx=2)
        
        btn_cobrar = ctk.CTkButton(
            btn_frame,
            text="Cobrar",
            width=100,
            height=35,
            fg_color="#1a73e8",  # Azul
            hover_color="#1557b0",
            command=self.procesar_venta
        )
        btn_cobrar.pack(side="left", padx=2)
        
        btn_limpiar = ctk.CTkButton(
            btn_frame,
            text="Limpiar",
            width=80,
            height=35,
            fg_color="#dc3545",  # Rojo
            hover_color="#c82333",
            command=self.limpiar_carrito
        )
        btn_limpiar.pack(side="left", padx=2)
        
        # === SECCIÓN DERECHA ===
        # Estadísticas del día
        stats_frame = ctk.CTkFrame(right_frame, fg_color="#f8f9fa", corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text="Estadísticas del Día",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#666666"
        )
        stats_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        stats_content = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_content.pack(fill="x", padx=10, pady=(0, 10))
        
        # Obtener estadísticas
        stats = self.venta_controller.obtener_estadisticas('hoy')
        
        self.lbl_ventas_hoy = ctk.CTkLabel(
            stats_content,
            text=f"Ventas hoy: {stats['resumen'].get('total_ventas', 0)}",
            font=ctk.CTkFont(size=13),
            text_color="#666666"
        )
        self.lbl_ventas_hoy.pack(anchor="w", pady=2)
        
        self.lbl_ingresos_hoy = ctk.CTkLabel(
            stats_content,
            text = f"Ingresos: ${(stats['resumen'].get('ingresos_totales') or 0):.2f}",
            font=ctk.CTkFont(size=13),
            text_color="#666666"
        )
        self.lbl_ingresos_hoy.pack(anchor="w", pady=2)
        
        # Ventas recientes
        recientes_label = ctk.CTkLabel(
            right_frame,
            text="Ventas Recientes",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#666666"
        )
        recientes_label.pack(anchor="w", pady=(10, 5))
        
        # Treeview para ventas recientes
        self.tree_recientes = ttk.Treeview(
            right_frame,
            columns=("Folio", "Total", "Hora"),
            show="tree headings",
            height=12
        )
        self.tree_recientes.heading("#0", text="ID")
        self.tree_recientes.heading("Folio", text="Folio")
        self.tree_recientes.heading("Total", text="Total")
        self.tree_recientes.heading("Hora", text="Hora")
        
        self.tree_recientes.column("#0", width=40)
        self.tree_recientes.column("Folio", width=120)
        self.tree_recientes.column("Total", width=80)
        self.tree_recientes.column("Hora", width=80)
        
        self.tree_recientes.pack(fill="both", expand=True)
        
        # Botón actualizar (azul)
        btn_actualizar = ctk.CTkButton(
            right_frame,
            text="Actualizar",
            width=100,
            height=30,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            command=self.actualizar_ventas_recientes
        )
        btn_actualizar.pack(pady=10)
        
        # Cargar ventas recientes
        self.actualizar_ventas_recientes()
        
    def buscar_productos(self, event=None):
        """Busca productos y actualiza la lista"""
        termino = self.entry_buscar.get()
        productos = self.producto_controller.buscar_productos(termino)
        self.actualizar_lista_productos(productos)
        
    def actualizar_lista_productos(self, productos):
        """Actualiza la lista de productos en el treeview"""
        # Limpiar treeview
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        # Agregar productos
        for prod in productos:
            self.tree_productos.insert(
                "",
                "end",
                text=prod.id,
                values=(prod.codigo, prod.nombre, f"${prod.precio_venta:.2f}", prod.stock)
            )
    
    def agregar_por_codigo(self, event=None):
        """Agrega producto al carrito por código"""
        codigo = self.entry_buscar.get().strip()
        if codigo:
            producto = self.producto_controller.obtener_producto_por_codigo(codigo)
            if producto:
                self.agregar_producto_al_carrito(producto, 1)
                self.entry_buscar.delete(0, "end")
            else:
                messagebox.showerror("Error", f"No se encontró producto con código {codigo}")
    
    def agregar_al_carrito(self, event):
        """Agrega producto seleccionado al carrito"""
        seleccion = self.tree_productos.selection()
        if seleccion:
            item = self.tree_productos.item(seleccion[0])
            producto_id = int(item['text'])
            producto = self.producto_controller.obtener_producto(producto_id)
            
            if producto:
                self.mostrar_dialogo_cantidad(producto)
    
    def mostrar_dialogo_cantidad(self, producto):
        """Muestra diálogo para ingresar cantidad"""
        ventana_principal = self.winfo_toplevel()
        
        dialog = ctk.CTkToplevel(ventana_principal)
        dialog.title("Cantidad")
        dialog.geometry("350x250")
        
        # --- CORRECCIÓN AQUÍ ---
        dialog.transient(ventana_principal)
        dialog.wait_visibility() # Esperar a que sea visible
        dialog.grab_set()
        dialog.focus_set()
        # -----------------------
        
        dialog.update_idletasks()
        x = ventana_principal.winfo_x() + (ventana_principal.winfo_width() // 2) - (350 // 2)
        y = ventana_principal.winfo_y() + (ventana_principal.winfo_height() // 2) - (250 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
        label = ctk.CTkLabel(
            dialog,
            text=f"Producto: {producto.nombre}\nStock disponible: {producto.stock}",
            font=ctk.CTkFont(size=13)
        )
        label.pack(pady=20)
        
        entry_cantidad = ctk.CTkEntry(
            dialog,
            placeholder_text="Cantidad",
            width=200,
            height=38,
            fg_color="white",
            border_color="#cccccc"
        )
        entry_cantidad.pack(pady=10)
        entry_cantidad.focus()

        def confirmar():
            try:
                cantidad = int(entry_cantidad.get())
                if cantidad > 0:
                    if cantidad <= producto.stock:
                        self.agregar_producto_al_carrito(producto, cantidad)
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", f"Stock insuficiente. Disponible: {producto.stock}", parent=dialog)
                else:
                    messagebox.showerror("Error", "La cantidad debe ser mayor a 0", parent=dialog)
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad válida", parent=dialog)

        entry_cantidad.bind("<Return>", lambda e: confirmar())
        
        # Estos botones ahora están fuera de la función confirmar() para que se vean
        btn_confirmar = ctk.CTkButton(
            dialog,
            text="Confirmar",
            width=120,
            height=38,
            fg_color="#28a745",
            hover_color="#218838",
            command=confirmar,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn_confirmar.pack(pady=10)
        
        btn_cancelar = ctk.CTkButton(
            dialog,
            text="Cancelar",
            width=120,
            height=38,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=dialog.destroy,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn_cancelar.pack(pady=5)
        
        dialog.lift()
    
    def agregar_producto_al_carrito(self, producto, cantidad):
        """Agrega un producto al carrito"""
        try:
            self.venta_actual.agregar_producto(producto, cantidad)
            self.actualizar_carrito()
            self.entry_buscar.delete(0, "end")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def quitar_del_carrito(self, event):
        """Quita producto seleccionado del carrito"""
        seleccion = self.tree_carrito.selection()
        if seleccion and self.venta_actual:
            item = self.tree_carrito.item(seleccion[0])
            producto_id = int(item['text'])
            
            if messagebox.askyesno("Confirmar", "¿Eliminar producto del carrito?"):
                self.venta_actual.quitar_producto(producto_id)
                self.actualizar_carrito()
    
    def limpiar_carrito(self):
        """Limpia el carrito de compras"""
        if self.carrito_items and messagebox.askyesno("Confirmar", "¿Limpiar el carrito?"):
            self.nueva_venta()
    
    def actualizar_carrito(self):
        """Actualiza la vista del carrito"""
        # Limpiar treeview
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        if self.venta_actual:
            # Agregar detalles
            for detalle in self.venta_actual.detalles:
                self.tree_carrito.insert(
                    "",
                    "end",
                    text=detalle.producto.id,
                    values=(
                        detalle.producto.nombre,
                        detalle.cantidad,
                        f"${detalle.precio_unitario:.2f}",
                        f"${detalle.subtotal:.2f}"
                    )
                )
            
            # Actualizar total
            self.lbl_total.configure(text=f"Total: ${self.venta_actual.total:.2f}")
    
    def nueva_venta(self):
        """Inicia una nueva venta"""
        self.venta_actual = Venta(usuario=self.usuario)
        self.carrito_items = []
        self.actualizar_carrito()
        self.entry_buscar.delete(0, "end")
        self.entry_buscar.focus()
        self.buscar_productos()
    
    def procesar_venta(self):
        """Procesa la venta actual"""
        if not self.venta_actual or not self.venta_actual.detalles:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito")
            return
        
        # Mostrar diálogo de confirmación
        if messagebox.askyesno(
            "Confirmar Venta",
            f"Total a cobrar: ${self.venta_actual.total:.2f}\n\n¿Confirmar la venta?"
        ):
            try:
                self.venta_actual.guardar()
                messagebox.showinfo("Éxito", f"Venta realizada con éxito\nFolio: {self.venta_actual.folio}")
                self.nueva_venta()
                self.actualizar_ventas_recientes()
                self.actualizar_estadisticas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar la venta: {str(e)}")
    
    def actualizar_ventas_recientes(self):
        """Actualiza la lista de ventas recientes"""
        ventas = self.venta_controller.obtener_ventas_hoy()
        
        # Limpiar treeview
        for item in self.tree_recientes.get_children():
            self.tree_recientes.delete(item)
        
        # Agregar ventas
        for venta in ventas:
            hora = venta.fecha.split()[1] if ' ' in venta.fecha else venta.fecha
            self.tree_recientes.insert(
                "",
                "end",
                text=venta.id,
                values=(venta.folio, f"${venta.total:.2f}", hora)
            )
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del día"""
        stats = self.venta_controller.obtener_estadisticas('hoy')
        self.lbl_ventas_hoy.configure(text=f"Ventas hoy: {stats['resumen'].get('total_ventas', 0)}")
        self.lbl_ingresos_hoy.configure(
            text=f"Ingresos: ${stats['resumen'].get('ingresos_totales', 0):.2f}"
        )