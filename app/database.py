import sqlite3
from pathlib import Path

# Chemin vers le fichier SQLite (à la racine du projet)
DB_PATH = Path(__file__).resolve().parent.parent / "calculs.db"


def get_connection() -> sqlite3.Connection:
    """Retourne une connexion SQLite avec accès aux colonnes par nom."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crée la table 'calculs' si elle n'existe pas."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calculs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_produit TEXT NOT NULL,
                cout_materiaux REAL NOT NULL,
                temps_heures REAL NOT NULL,
                taux_horaire REAL NOT NULL,
                marge REAL NOT NULL,
                prix_final REAL NOT NULL,
                date_creation TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()