# Calculateur de prix pour artisans malgaches

Petit outil web pour aider les artisans malgaches (vannerie, couture, menuiserie, broderie…) à calculer un prix de vente juste en tenant compte :

- du coût des matières premières,
- des frais divers (main-d'œuvre indirecte, transport, etc.),
- du temps de travail,
- du taux horaire,
- de la marge souhaitée.

L'application calcule automatiquement le prix de revient et le prix de vente conseillé, gère plusieurs devises, propose des profils de marge par métier, arrondit automatiquement au millier d'Ariary, et conserve un historique exportable en CSV.

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
- **Export CSV de l'historique** : http://127.0.0.1:8000/api/export.csv

---

## Comment sont calculés les prix ?

Soit :

- `M` = coût des matériaux
- `F` = frais divers
- `H` = temps de travail (heures)
- `T` = taux horaire
- `G` = marge souhaitée (%)

**Formules :**

```
Prix de revient = M + F + (H × T)
Prix de vente   = Prix de revient × (1 + G / 100)
```

Si la devise est l'Ariary (MGA), le prix de vente est arrondi au millier d'Ariary le plus proche. Pour l'Euro et le Dollar, l'arrondi se fait au centime.

### Exemple concret

| Champ | Valeur |
|---|---|
| Nom du produit | Panier en raphia |
| Métier | Vannerie |
| Devise | Ariary (MGA) |
| Coût des matériaux | 5 000 Ar |
| Frais divers | 500 Ar |
| Temps de travail | 3 h |
| Taux horaire | 2 000 Ar/h |
| Marge souhaitée | 30 % |

**Calcul :**

```
Prix de revient = 5 000 + 500 + (3 × 2 000) = 11 500 Ar
Prix de vente   = 11 500 × 1,30             = 14 950 Ar
Arrondi millier = 15 000 Ar
```

**Prix conseillé : 15 000 Ar**

---

## Fonctionnalités

- Formulaire de saisie complet : nom, métier, devise, matériaux, frais divers, temps, taux horaire, marge
- Raccourcis de marge : 20 %, 30 %, 40 %, 50 %
- Calcul automatique du prix de revient et du prix de vente conseillé
- Multi-devises : Ariary (MGA), Euro (EUR), Dollar (USD)
- Profils de métier : vannerie, couture, menuiserie, broderie, autre
- Arrondi automatique au millier d'Ariary le plus proche
- Sauvegarde en SQLite
- Historique consultable et rafraîchissable
- Export CSV de l'historique
- Interface responsive, en français, sobre et accessible

---

## Endpoints de l'API

| Méthode | URL | Description |
|---|---|---|
| GET | `/` | Sert l'interface `index.html` |
| POST | `/api/calcul` | Reçoit les données, calcule, sauvegarde et retourne le résultat |
| GET | `/api/historique` | Retourne la liste des calculs enregistrés |
| GET | `/api/export.csv` | Télécharge l'historique au format CSV |

### Exemple d'appel `POST /api/calcul`

```bash
curl -X POST http://127.0.0.1:8000/api/calcul \
  -H "Content-Type: application/json" \
  -d '{
    "nom_produit": "Panier en raphia",
    "metier": "vannerie",
    "devise": "MGA",
    "cout_materiaux": 5000,
    "frais_divers": 500,
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
  "metier": "vannerie",
  "devise": "MGA",
  "cout_materiaux": 5000.0,
  "frais_divers": 500.0,
  "temps_heures": 3.0,
  "taux_horaire": 2000.0,
  "marge": 30.0,
  "prix_revient": 11500.0,
  "prix_final": 15000.0,
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
| metier | TEXT | Métier associé |
| devise | TEXT | Devise (MGA, EUR, USD) |
| cout_materiaux | REAL | Coût des matériaux |
| frais_divers | REAL | Frais divers |
| temps_heures | REAL | Temps de travail (heures) |
| taux_horaire | REAL | Taux horaire |
| marge | REAL | Marge appliquée (%) |
| prix_revient | REAL | Prix de revient |
| prix_final | REAL | Prix de vente conseillé |
| date_creation | TEXT | Date ISO de création |

> ⚠️ Si vous aviez une ancienne version de `calculs.db`, supprimez-la avant de relancer l'application : le schéma a changé.

---

## Vérification

- [x] Le serveur démarre avec `uvicorn app.main:app --reload`
- [x] L'interface s'affiche sur http://127.0.0.1:8000
- [x] On peut saisir un produit, choisir un métier et une devise, obtenir un prix conseillé
- [x] Le calcul est sauvegardé dans SQLite
- [x] L'historique affiche les calculs enregistrés
- [x] L'export CSV télécharge un fichier `historique_calculs.csv`
- [x] Les endpoints sont visibles dans `/docs`

---

## Licence

Projet pédagogique : libre d'utilisation et de modification.

---

## Étapes à exécuter

1. Remplace le contenu des **7 fichiers** ci-dessus.
2. Supprime l'ancienne base si elle existe :

```bash
rm -f calculs.db
```

3. Relance :

```bash
uvicorn app.main:app --reload
```

4. Ouvre http://127.0.0.1:8000 et teste.