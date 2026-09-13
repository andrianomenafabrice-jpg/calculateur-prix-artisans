from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import get_connection, init_db
from app.models import CalculInput, CalculOutput

app = FastAPI(title="Calculateur de prix pour artisans")

# Dossier static
STATIC_DIR = Path(__file__).resolve().parent / "static"


# ---------- Initialisation ----------
@app.on_event("startup")
def on_startup() -> None:
    init_db()


# ---------- Interface web ----------
@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html introuvable")
    return FileResponse(index_file)


# ---------- API : calcul + sauvegarde ----------
@app.post("/api/calcul", response_model=CalculOutput)
def calculer(payload: CalculInput) -> CalculOutput:
    # 1. Calcul du prix de revient
    prix_revient = payload.cout_materiaux + (payload.temps_heures * payload.taux_horaire)

    # 2. Calcul du prix de vente conseillé
    prix_final = prix_revient * (1 + payload.marge / 100)

    # 3. Sauvegarde en base
    date_creation = datetime.now().isoformat(timespec="seconds")

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO calculs (
                nom_produit, cout_materiaux, temps_heures,
                taux_horaire, marge, prix_final, date_creation
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.nom_produit,
                payload.cout_materiaux,
                payload.temps_heures,
                payload.taux_horaire,
                payload.marge,
                prix_final,
                date_creation,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
    finally:
        conn.close()

    return CalculOutput(
        id=new_id,
        nom_produit=payload.nom_produit,
        cout_materiaux=payload.cout_materiaux,
        temps_heures=payload.temps_heures,
        taux_horaire=payload.taux_horaire,
        marge=payload.marge,
        prix_final=round(prix_final, 2),
        date_creation=date_creation,
    )


# ---------- API : historique ----------
@app.get("/api/historique", response_model=list[CalculOutput])
def historique() -> list[CalculOutput]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, nom_produit, cout_materiaux, temps_heures,
                   taux_horaire, marge, prix_final, date_creation
            FROM calculs
            ORDER BY id DESC
            """
        ).fetchall()
    finally:
        conn.close()

    return [CalculOutput(**dict(row)) for row in rows]


# ---------- Fichiers statiques (CSS / JS) ----------
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")