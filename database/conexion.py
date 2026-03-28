# database/conexion.py
import sqlite3
import os
from pathlib import Path

class Database:
    """
    Clase para gestionar la conexión a la base de datos SQLite.
    Implementa el patrón Singleton para mantener una sola conexión activa.
    """
    _instance = None
    _conn = None

    def __new__(cls, *args, **kwargs):
        """Asegura que solo haya una instancia de la clase Database."""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_name="gestion_ventas.db"):
        """
        Inicializa la conexión a la base de datos.
        Args:
            db_name (str): Nombre del archivo de la base de datos.
        """
        # Solo conectar si no hay una conexión activa
        if self._conn is None:
            # Obtener la ruta absoluta del directorio del proyecto
            # Esto asegura que la DB se cree en la raíz del proyecto y no en directorios temporales
            base_dir = Path(__file__).parent.parent
            db_path = base_dir / db_name

            print(f"📁 Conectando a la base de datos en: {db_path}")
            try:
                self._conn = sqlite3.connect(str(db_path))
                # Importante: Permite trabajar con filas como diccionarios (acceso por nombre de columna)
                self._conn.row_factory = sqlite3.Row
                # Habilitar foreign keys para mantener la integridad de los datos
                self._conn.execute("PRAGMA foreign_keys = ON")
                print("✅ Conexión a base de datos establecida.")
            except sqlite3.Error as e:
                print(f"❌ Error al conectar a la base de datos: {e}")
                self._conn = None

    def get_connection(self):
        """Devuelve la conexión activa."""
        if self._conn is None:
            raise Exception("No hay conexión a la base de datos.")
        return self._conn

    def close_connection(self):
        """Cierra la conexión a la base de datos."""
        if self._conn:
            self._conn.close()
            self._conn = None
            print("🔌 Conexión a base de datos cerrada.")

    def execute_query(self, query, params=()):
        """
        Ejecuta una consulta SQL (INSERT, UPDATE, DELETE) y hace commit.
        Args:
            query (str): La consulta SQL.
            params (tuple): Los parámetros para la consulta.
        Returns:
            int: El id de la última fila insertada o None si hubo error.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Error en execute_query: {e}")
            conn.rollback() # Revertir cambios en caso de error
            return None

    def fetch_all(self, query, params=()):
        """
        Ejecuta una consulta SELECT y devuelve todas las filas.
        Returns:
            list: Lista de filas como objetos Row (acceso por clave/índice).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error en fetch_all: {e}")
            return []

    def fetch_one(self, query, params=()):
        """
        Ejecuta una consulta SELECT y devuelve la primera fila.
        Returns:
            sqlite3.Row: La primera fila o None si no hay resultados.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Error en fetch_one: {e}")
            return None
