# Calculateur de prix pour artisans

Petit outil web pour aider les artisans malgaches à calculer un prix de vente juste en tenant compte des matériaux, du temps de travail et de la marge.

## Stack
- Python / FastAPI
- SQLite
- HTML / CSS / JavaScript vanilla

## Lancer le projet en local
```bash
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload