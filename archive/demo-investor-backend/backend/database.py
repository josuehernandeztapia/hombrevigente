"""
Database utilities - Conexión a SQLite
Reutiliza la DB generada por generador_sintetico_v2.py
"""
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

# Path a la DB (un nivel arriba de backend/)
DB_PATH = Path(__file__).parent.parent / "demo_hombrevigente.db"


def get_connection():
    """Obtiene conexión a SQLite"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
    return conn


def get_cliente_by_id(cliente_id: str) -> Optional[Dict]:
    """Obtiene un cliente por ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE cliente_id = ?", (cliente_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_random_cliente() -> Dict:
    """Obtiene un cliente aleatorio"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def get_diagnosticos_by_cliente(cliente_id: str) -> List[Dict]:
    """Obtiene diagnósticos de un cliente"""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM diagnosticos WHERE cliente_id = ? ORDER BY fecha_diagnostico DESC",
        conn,
        params=(cliente_id,)
    )
    conn.close()
    return df.to_dict('records')


def get_eventos_by_cliente(cliente_id: str) -> List[Dict]:
    """Obtiene eventos de compra de un cliente"""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM eventos WHERE cliente_id = ? ORDER BY fecha_evento DESC",
        conn,
        params=(cliente_id,)
    )
    conn.close()
    return df.to_dict('records')


def insert_diagnostico(data: Dict) -> str:
    """Inserta un nuevo diagnóstico"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO diagnosticos (
            diagnostico_id, cliente_id, fecha_diagnostico,
            indice_vigente, subscore_estructural, subscore_piel, subscore_biologico,
            interpretacion, recomendaciones, hardware_usado, ml_model_version, processing_time_sec
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['diagnostico_id'], data['cliente_id'], data['fecha_diagnostico'],
        data['indice_vigente'], data['subscore_estructural'], data['subscore_piel'], data['subscore_biologico'],
        data['interpretacion'], data['recomendaciones'],
        data['hardware_usado'], data['ml_model_version'], data['processing_time_sec']
    ))

    conn.commit()
    conn.close()
    return data['diagnostico_id']
