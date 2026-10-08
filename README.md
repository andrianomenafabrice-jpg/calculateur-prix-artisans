# Calculateur de prix pour artisans malgaches

Un outil web local qui calcule le prix de vente juste d'un produit artisanal
à partir des matériaux, du temps de travail et de la marge souhaitée.
Génère aussi un devis PDF à remettre au client.

## Ce que ça fait

- Calcul du prix de revient et du prix de vente conseillé
- Multi-devises : Ariary, Euro, Dollar
- Profils de métier : vannerie, couture, menuiserie, broderie
- Arrondi automatique au millier d'Ariary
- Historique des calculs + export CSV
- Devis PDF prêt à remettre au client

## Stack

- Python / FastAPI
- SQLite
- ReportLab (PDF)
- HTML / CSS / JavaScript vanilla

## Lancer en local

```bash
python -m venv venv
source venv/Scripts/activate   # Git Bash (Windows) — sinon : venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
Ouvrir : http://127.0.0.1:8000

Utiliser l'application
Remplir le formulaire (produit, métier, devise, matériaux, frais, temps, taux horaire, marge).

Cliquer sur Calculer et enregistrer.

Le calcul apparaît dans l'historique à droite.

Cliquer sur Devis PDF sur une ligne pour générer le devis.

Comment le prix est calculé
text
Prix de revient = matériaux + frais divers + (heures × taux horaire)
Prix de vente   = prix de revient × (1 + marge / 100)
Si la devise est l'Ariary, le prix final est arrondi au millier le plus proche.

Exemple : 5 000 + 500 + (3 × 2 000) = 11 500 Ar de revient
11 500 × 1,30 = 14 950 Ar → arrondi à 15 000 Ar

Endpoints
Méthode	URL	Description
GET	/	Interface web
POST	/api/calcul	Calculer et sauvegarder
GET	/api/historique	Liste des calculs
GET	/api/export.csv	Export CSV de l'historique
GET	/api/devis/{id}.pdf	Générer un devis PDF
Structure
text
calculateur-prix-artisans/
├── app/
│   ├── main.py       # API FastAPI
│   ├── database.py   # SQLite
│   ├── models.py     # Schémas Pydantic
│   ├── pdf.py        # Génération PDF
│   └── static/       # Interface (HTML/CSS/JS)
├── requirements.txt
└── README.md
Licence
Projet pédagogique, libre d'utilisation et de modification.