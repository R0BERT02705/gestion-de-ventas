# controllers/venta_controller.py
from models import Venta
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import sqlite3

class VentaController:
    """Controlador para manejar operaciones con ventas."""

    def __init__(self):
        """Inicializa el controlador sin crear conexiones persistentes"""
        pass

    def obtener_ventas_hoy(self) -> List[Venta]:
        """Obtiene las ventas del día actual."""
        hoy = datetime.now().strftime('%Y-%m-%d')
        manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        return Venta.listar_por_fecha(hoy, manana)

    def obtener_ventas_semana(self) -> List[Venta]:
        """Obtiene las ventas de la última semana."""
        fin = datetime.now()
        inicio = fin - timedelta(days=7)
        return Venta.listar_por_fecha(
            inicio.strftime('%Y-%m-%d'),
            fin.strftime('%Y-%m-%d')
        )

    def obtener_ventas_mes(self) -> List[Venta]:
        """Obtiene las ventas del mes actual."""
        fin = datetime.now()
        inicio = fin.replace(day=1)
        return Venta.listar_por_fecha(
            inicio.strftime('%Y-%m-%d'),
            fin.strftime('%Y-%m-%d')
        )

    def obtener_ventas_por_vendedor(self, usuario_id: int, limite=50) -> List[Venta]:
        """Obtiene las ventas de un vendedor específico."""
        return Venta.listar_por_vendedor(usuario_id, limite)

    def obtener_estadisticas(self, periodo='mes') -> Dict:
        """
        Obtiene estadísticas de ventas.
        periodos: 'hoy', 'semana', 'mes', 'año'
        """
        try:
            hoy = datetime.now()
            
            if periodo == 'hoy':
                inicio = hoy.strftime('%Y-%m-%d')
                fin = hoy.strftime('%Y-%m-%d')
            elif periodo == 'semana':
                inicio = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
                fin = hoy.strftime('%Y-%m-%d')
            elif periodo == 'mes':
                inicio = hoy.replace(day=1).strftime('%Y-%m-%d')
                fin = hoy.strftime('%Y-%m-%d')
            elif periodo == 'año':
                inicio = hoy.replace(month=1, day=1).strftime('%Y-%m-%d')
                fin = hoy.strftime('%Y-%m-%d')
            else:
                inicio = None
                fin = None

            return Venta.obtener_estadisticas(inicio, fin)
        except sqlite3.Error as e:
            print(f"Error SQLite en obtener_estadisticas: {e}")
            return {'total_ventas': 0, 'cantidad_ventas': 0, 'ticket_promedio': 0}

    def obtener_venta(self, venta_id: int) -> Optional[Venta]:
        """Obtiene una venta por su ID."""
        return Venta.obtener_por_id(venta_id)

    def buscar_por_folio(self, folio: str) -> Optional[Venta]:
        """Busca una venta por su folio."""
        return Venta.obtener_por_folio(folio)