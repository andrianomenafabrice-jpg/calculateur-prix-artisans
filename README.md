# Calculateur de prix pour artisans malgaches

Petit outil web pour aider les artisans malgaches (vannerie, couture, menuiserie, broderie…) à calculer un prix de vente juste en tenant compte :

- du coût des matières premières,
- du temps de travail,
- du taux horaire,
- de la marge souhaitée.

L'application calcule automatiquement le prix de revient et le prix de vente conseillé, puis conserve un historique des calculs.

---

## Stack technique

- **Python 3.10+**
- **FastAPI** : API web rapide et légère
- **SQLite** : base de données locale, aucun serveur à installer
- **HTML / CSS / JavaScript vanilla** : pas de framework frontend
- **Uvicorn** : serveur ASGI pour lancer l'application

---

## Structure du projet

```
calculateur-prix-artisans/
├── app/
│   ├── __init__.py
│   ├── main.py           # API FastAPI + endpoints
│   ├── database.py       # Connexion SQLite + création de la table
│   ├── models.py         # Schémas Pydantic (entrée / sortie)
│   └── static/
│       ├── index.html    # Interface utilisateur
│       ├── style.css     # Styles
│       └── app.js        # Logique côté client
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation et lancement

### 1. Cloner le dépôt

```bash
git clone <URL_DU_REPO_GITHUB>
cd calculateur-prix-artisans
```

### 2. Créer et activer un environnement virtuel

**Linux / macOS / Git Bash (Windows) :**

```bash
python -m venv venv
source venv/Scripts/activate   # Git Bash sous Windows
# ou
source venv/bin/activate       # Linux / macOS
```

**Windows (PowerShell / cmd) :**

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer le serveur

```bash
uvicorn app.main:app --reload
```

### 5. Ouvrir l'application

Dans le navigateur :

- **Application** : http://127.0.0.1:8000
- **Documentation interactive de l'API** : http://127.0.0.1:8000/docs

---

## Comment sont calculés les prix ?

Soit :

- `M` = coût des matériaux (Ar)
- `H` = temps de travail (heures)
- `T` = taux horaire (Ar/h)
- `G` = marge souhaitée (%)

**Formules :**

```
Prix de revient = M + (H × T)
Prix de vente   = Prix de revient × (1 + G / 100)
```

### Exemple concret

| Champ | Valeur |
|---|---|
| Nom du produit | Panier en raphia |
| Coût des matériaux | 5 000 Ar |
| Temps de travail | 3 h |
| Taux horaire | 2 000 Ar/h |
| Marge souhaitée | 30 % |

**Calcul :**

```
Prix de revient = 5 000 + (3 × 2 000) = 11 000 Ar
Prix de vente   = 11 000 × 1,30       = 14 300 Ar
```

**Prix conseillé : 14 300 Ar**

---

## Endpoints de l'API

| Méthode | URL | Description |
|---|---|---|
| GET | `/` | Sert l'interface `index.html` |
| POST | `/api/calcul` | Reçoit les données, calcule, sauvegarde et retourne le résultat |
| GET | `/api/historique` | Retourne la liste des calculs enregistrés |

### Exemple d'appel `POST /api/calcul`

```bash
curl -X POST http://127.0.0.1:8000/api/calcul \
  -H "Content-Type: application/json" \
  -d '{
    "nom_produit": "Panier en raphia",
    "cout_materiaux": 5000,
    "temps_heures": 3,
    "taux_horaire": 2000,
    "marge": 30
  }'
```

**Réponse :**

```json
{
  "id": 1,
  "nom_produit": "Panier en raphia",
  "cout_materiaux": 5000.0,
  "temps_heures": 3.0,
  "taux_horaire": 2000.0,
  "marge": 30.0,
  "prix_final": 14300.0,
  "date_creation": "2025-01-15T10:23:45"
}
```

---

## Base de données

Fichier SQLite créé automatiquement au premier lancement : `calculs.db` (à la racine du projet).

**Table `calculs` :**

| Colonne | Type | Description |
|---|---|---|
| id | INTEGER | Clé primaire auto-incrémentée |
| nom_produit | TEXT | Nom du produit |
| cout_materiaux | REAL | Coût des matériaux (Ar) |
| temps_heures | REAL | Temps de travail (heures) |
| taux_horaire | REAL | Taux horaire (Ar/h) |
| marge | REAL | Marge appliquée (%) |
| prix_final | REAL | Prix de vente conseillé (Ar) |
| date_creation | TEXT | Date ISO de création |

---

## Vérification du MVP

- [x] Le serveur démarre avec `uvicorn app.main:app --reload`
- [x] L'interface s'affiche sur http://127.0.0.1:8000
- [x] On peut saisir un produit et obtenir un prix conseillé
- [x] Le calcul est sauvegardé dans SQLite
- [x] L'historique affiche les calculs enregistrés
- [x] L'interface est responsive et en français
- [x] Les endpoints sont visibles dans `/docs`

---

## Pistes d'amélioration future

- Export CSV ou PDF des devis pour les artisans
- Gestion de plusieurs devises (Ariary, Euro, Dollar)
- Profils de marge par métier (vannerie, couture, menuiserie…)
- Champ « frais divers » ou « main-d'œuvre indirecte »
- Arrondi automatique au millier d'Ariary le plus proche

---

## Licence

Projet pédagogique : libre d'utilisation et de modification.
