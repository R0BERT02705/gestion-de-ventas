# main.py
import customtkinter as ctk
from views.login_view import LoginView
from database.init_db import init_database
import os
from pathlib import Path

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MainApplication:
    def __init__(self):
        db_path = Path(__file__).parent / "gestion_ventas.db"
        if not db_path.exists():
            print("📦 Base de datos no encontrada. Inicializando...")
            try:
                init_database()
            except Exception as e:
                from tkinter import messagebox
                if not messagebox.askyesno("Error", f"Error: {e}\n¿Continuar?"):
                    exit(1)
        
        self.root = ctk.CTk()
        self.root.title("Sistema de Ventas - Punto de Venta")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Guardamos una referencia de la app en el root para acceder desde las vistas
        self.root.app_instance = self
        
        self.center_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.show_login()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_login(self):
        """Muestra la vista de inicio de sesión limpiando la pantalla"""
        # Limpiar cualquier widget existente en el root para evitar pantallas blancas/encimadas
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.title("Sistema de Ventas - Inicio de Sesión")
        self.login_view = LoginView(self.root, self.on_login_success)
        self.login_view.pack(fill="both", expand=True)
    
    def on_login_success(self, usuario):
        """Callback ejecutado cuando el inicio de sesión es exitoso"""
        # Limpiar pantalla
        for widget in self.root.winfo_children():
            widget.destroy()
        
        from views.main_view import MainView
        self.main_view = MainView(self.root, usuario)
        self.main_view.pack(fill="both", expand=True)
        self.root.title(f"Sistema de Ventas - Usuario: {usuario.nombre_completo}")
    
    def on_closing(self):
        from tkinter import messagebox
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir del sistema?"):
            self.cleanup()
            self.root.destroy()
    
    def cleanup(self):
        print("🧹 Limpiando recursos...")
        try:
            from database.conexion import Database
            Database().close_connection()
        except: pass
        try:
            from utils.session import Session
            Session().limpiar()
        except: pass

    def run(self):
        print("🚀 Iniciando Sistema de Ventas...")
        self.root.mainloop()

def main():
    app = MainApplication()
    app.run()

if __name__ == "__main__":
    main()