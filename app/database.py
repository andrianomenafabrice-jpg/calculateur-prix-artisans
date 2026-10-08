# app/database.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "calculs.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calculs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_produit TEXT NOT NULL,
                metier TEXT NOT NULL DEFAULT 'autre',
                devise TEXT NOT NULL DEFAULT 'MGA',
                cout_materiaux REAL NOT NULL,
                frais_divers REAL NOT NULL DEFAULT 0,
                temps_heures REAL NOT NULL,
                taux_horaire REAL NOT NULL,
                marge REAL NOT NULL,
                prix_revient REAL NOT NULL,
                prix_final REAL NOT NULL,
                date_creation TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()