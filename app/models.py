# app/models.py
from pydantic import BaseModel, Field
from typing import Literal


Devise = Literal["MGA", "EUR", "USD"]
Metier = Literal["vannerie", "couture", "menuiserie", "broderie", "autre"]


class CalculInput(BaseModel):
    nom_produit: str = Field(..., min_length=1, max_length=120)
    metier: Metier = "autre"
    devise: Devise = "MGA"
    cout_materiaux: float = Field(..., ge=0)
    frais_divers: float = Field(0, ge=0)
    temps_heures: float = Field(..., ge=0)
    taux_horaire: float = Field(..., ge=0)
    marge: float = Field(..., ge=0)


class CalculOutput(BaseModel):
    id: int
    nom_produit: str
    metier: str
    devise: str
    cout_materiaux: float
    frais_divers: float
    temps_heures: float
    taux_horaire: float
    marge: float
    prix_revient: float
    prix_final: float
    date_creation: str