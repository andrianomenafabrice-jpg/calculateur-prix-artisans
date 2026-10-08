import csv
import io
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles

from app.database import get_connection, init_db
from app.models import CalculInput, CalculOutput
from app.pdf import generer_devis_pdf

app = FastAPI(title="Calculateur de prix pour artisans")

STATIC_DIR = Path(__file__).resolve().parent / "static"


def arrondi_millier(valeur: float, devise: str) -> float:
    if devise == "MGA":
        return round(valeur / 1000) * 1000
    return round(valeur, 2)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html introuvable")
    return FileResponse(index_file)


@app.post("/api/calcul", response_model=CalculOutput)
def calculer(payload: CalculInput) -> CalculOutput:
    prix_revient = (
        payload.cout_materiaux
        + payload.frais_divers
        + (payload.temps_heures * payload.taux_horaire)
    )
    prix_final_brut = prix_revient * (1 + payload.marge / 100)
    prix_final = arrondi_millier(prix_final_brut, payload.devise)

    date_creation = datetime.now().isoformat(timespec="seconds")

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO calculs (
                nom_produit, metier, devise, cout_materiaux, frais_divers,
                temps_heures, taux_horaire, marge,
                prix_revient, prix_final, date_creation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.nom_produit,
                payload.metier,
                payload.devise,
                payload.cout_materiaux,
                payload.frais_divers,
                payload.temps_heures,
                payload.taux_horaire,
                payload.marge,
                round(prix_revient, 2),
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
        metier=payload.metier,
        devise=payload.devise,
        cout_materiaux=payload.cout_materiaux,
        frais_divers=payload.frais_divers,
        temps_heures=payload.temps_heures,
        taux_horaire=payload.taux_horaire,
        marge=payload.marge,
        prix_revient=round(prix_revient, 2),
        prix_final=prix_final,
        date_creation=date_creation,
    )


@app.get("/api/historique", response_model=list[CalculOutput])
def historique() -> list[CalculOutput]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, nom_produit, metier, devise, cout_materiaux, frais_divers,
                   temps_heures, taux_horaire, marge,
                   prix_revient, prix_final, date_creation
            FROM calculs
            ORDER BY id DESC
            """
        ).fetchall()
    finally:
        conn.close()
    return [CalculOutput(**dict(row)) for row in rows]


def _fetch_calcul(calcul_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT id, nom_produit, metier, devise, cout_materiaux, frais_divers,
                   temps_heures, taux_horaire, marge,
                   prix_revient, prix_final, date_creation
            FROM calculs
            WHERE id = ?
            """,
            (calcul_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Calcul introuvable")
    return dict(row)


@app.get("/api/devis/{calcul_id}.pdf")
def devis_pdf(
    calcul_id: int,
    artisan: str = Query("", max_length=120),
    client: str = Query("", max_length=120),
):
    calcul = _fetch_calcul(calcul_id)
    pdf_bytes = generer_devis_pdf(calcul, artisan=artisan, client=client)

    nom_fichier = f"devis_{calcul_id:05d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nom_fichier}"'
        },
    )


@app.get("/api/export.csv")
def export_csv():
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, nom_produit, metier, devise, cout_materiaux, frais_divers,
                   temps_heures, taux_horaire, marge,
                   prix_revient, prix_final, date_creation
            FROM calculs
            ORDER BY id DESC
            """
        ).fetchall()
    finally:
        conn.close()

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow([
        "id", "nom_produit", "metier", "devise", "cout_materiaux",
        "frais_divers", "temps_heures", "taux_horaire", "marge",
        "prix_revient", "prix_final", "date_creation",
    ])
    for row in rows:
        writer.writerow(list(row))

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=historique_calculs.csv"
        },
    )


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")