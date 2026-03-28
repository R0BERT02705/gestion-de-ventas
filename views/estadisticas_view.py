# views/estadisticas_view.py
import customtkinter as ctk
from controllers.venta_controller import VentaController
from datetime import datetime

class EstadisticasView(ctk.CTkFrame):
    def __init__(self, parent, usuario):
        super().__init__(parent, fg_color="white")
        self.usuario = usuario
        self.controlador = VentaController()
        self.setup_ui()
        # Primera carga después de que la UI esté lista
        self.after(500, self.cargar_datos_iniciales)

    def setup_ui(self):
        # Título
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="RESUMEN GENERAL DE VENTAS", 
            font=ctk.CTkFont(size=24, weight="bold"), 
            text_color="#1a73e8"
        )
        self.label_titulo.pack(pady=(30, 10))

        # Frame para las tarjetas
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=50, pady=20)
        
        # Configurar grid para 3 columnas
        for i in range(3): 
            self.cards_frame.grid_columnconfigure(i, weight=1)

        # Crear tarjetas con indicadores de carga
        self.lbl_total_val = self.crear_tarjeta(
            self.cards_frame, "TOTAL VENDIDO", "CARGANDO...", "#28a745", 0
        )
        self.lbl_cantidad_val = self.crear_tarjeta(
            self.cards_frame, "NÚM. VENTAS", "CARGANDO...", "#17a2b8", 1
        )
        self.lbl_promedio_val = self.crear_tarjeta(
            self.cards_frame, "PROMEDIO POR VENTA", "CARGANDO...", "#ffc107", 2
        )

        # Frame para botones
        self.botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.botones_frame.pack(pady=30)

        # Botón actualizar
        self.btn_refresh = ctk.CTkButton(
            self.botones_frame, 
            text="🔄 ACTUALIZAR DATOS", 
            command=self.ejecutar_actualizacion,
            fg_color="#1a73e8", 
            height=40,
            width=200
        )
        self.btn_refresh.pack(side="left", padx=10)

        # Selector de período
        self.periodo_var = ctk.StringVar(value="mes")
        self.periodo_menu = ctk.CTkOptionMenu(
            self.botones_frame,
            values=["hoy", "semana", "mes", "año"],
            variable=self.periodo_var,
            command=self.cambiar_periodo,
            fg_color="#6c757d",
            button_color="#495057",
            width=150,
            height=40
        )
        self.periodo_menu.pack(side="left", padx=10)

        # Label para mostrar errores
        self.error_label = ctk.CTkLabel(
            self, 
            text="", 
            font=ctk.CTkFont(size=12), 
            text_color="#dc3545"
        )
        self.error_label.pack(pady=10)

    def crear_tarjeta(self, parent, titulo, valor_inicial, color_tema, columna):
        """Crea una tarjeta de estadística"""
        frame = ctk.CTkFrame(
            parent, 
            fg_color="#f8f9fa", 
            border_width=2, 
            border_color=color_tema, 
            corner_radius=15
        )
        frame.grid(row=0, column=columna, padx=15, pady=10, sticky="nsew")
        
        # Título de la tarjeta
        ctk.CTkLabel(
            frame, 
            text=titulo, 
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(20, 5))
        
        # Valor de la tarjeta
        lbl_val = ctk.CTkLabel(
            frame, 
            text=valor_inicial, 
            font=ctk.CTkFont(size=26, weight="bold"), 
            text_color=color_tema
        )
        lbl_val.pack(pady=(0, 20))
        
        return lbl_val

    def cargar_datos_iniciales(self):
        """Carga inicial de datos"""
        self.ejecutar_actualizacion()

    def cambiar_periodo(self, periodo):
        """Cuando cambia el período, actualizar datos"""
        self.ejecutar_actualizacion()

    def ejecutar_actualizacion(self):
        """Ejecuta la actualización de estadísticas"""
        # Deshabilitar controles
        self.btn_refresh.configure(state="disabled", text="⏳ CARGANDO...")
        self.periodo_menu.configure(state="disabled")
        self.error_label.configure(text="")
        
        # Cambiar texto de las tarjetas a "CARGANDO..."
        self.lbl_total_val.configure(text="CARGANDO...")
        self.lbl_cantidad_val.configure(text="CARGANDO...")
        self.lbl_promedio_val.configure(text="CARGANDO...")
        
        # Obtener el período seleccionado
        periodo = self.periodo_var.get()
        
        try:
            # Obtener estadísticas directamente del controlador
            stats = self.controlador.obtener_estadisticas(periodo=periodo)
            
            # Extraer datos según la estructura de venta.py
            # En venta.py, obtener_estadisticas devuelve un diccionario con clave 'resumen'
            if 'resumen' in stats:
                # Si viene con la estructura de venta.py original
                resumen = stats['resumen']
                total = float(resumen.get('ingresos_totales', 0))
                cantidad = int(resumen.get('total_ventas', 0))
                promedio = float(resumen.get('ticket_promedio', 0))
            else:
                # Si viene con la estructura simplificada
                total = float(stats.get('total_ventas', 0))
                cantidad = int(stats.get('cantidad_ventas', 0))
                promedio = float(stats.get('ticket_promedio', 0))
            
            # Actualizar UI
            self.finalizar_carga(total, cantidad, promedio)
            
            # Mostrar mensaje si no hay datos
            if cantidad == 0:
                self.error_label.configure(
                    text="ℹ️ No hay ventas en el período seleccionado",
                    text_color="#17a2b8"
                )
            
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            import traceback
            traceback.print_exc()
            
            self.error_label.configure(
                text=f"❌ Error: {str(e)[:100]}",
                text_color="#dc3545"
            )
            self.finalizar_carga(0, 0, 0)

    def finalizar_carga(self, total, cantidad, promedio):
        """Finaliza la carga actualizando la UI"""
        try:
            # Formatear valores
            total_formateado = f"${total:,.2f}" if total > 0 else "$0.00"
            cantidad_formateada = f"{cantidad:,}" if cantidad > 0 else "0"
            promedio_formateado = f"${promedio:,.2f}" if promedio > 0 else "$0.00"
            
            # Actualizar labels
            self.lbl_total_val.configure(text=total_formateado)
            self.lbl_cantidad_val.configure(text=cantidad_formateada)
            self.lbl_promedio_val.configure(text=promedio_formateado)
            
        except Exception as e:
            print(f"Error actualizando UI: {e}")
            self.lbl_total_val.configure(text="$0.00")
            self.lbl_cantidad_val.configure(text="0")
            self.lbl_promedio_val.configure(text="$0.00")
        
        finally:
            # Restaurar controles
            self.btn_refresh.configure(state="normal", text="🔄 ACTUALIZAR DATOS")
            self.periodo_menu.configure(state="normal")