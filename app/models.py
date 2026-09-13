from pydantic import BaseModel, Field


class CalculInput(BaseModel):
    """Données envoyées par le formulaire web."""
    nom_produit: str = Field(..., min_length=1, max_length=120)
    cout_materiaux: float = Field(..., ge=0)
    temps_heures: float = Field(..., ge=0)
    taux_horaire: float = Field(..., ge=0)
    marge: float = Field(..., ge=0)


class CalculOutput(BaseModel):
    """Données renvoyées après calcul et sauvegarde."""
    id: int
    nom_produit: str
    cout_materiaux: float
    temps_heures: float
    taux_horaire: float
    marge: float
    prix_final: float
    date_creation: str