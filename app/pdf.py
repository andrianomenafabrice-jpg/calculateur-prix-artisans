from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


DEVISE_SYMBOLE = {"MGA": "Ar", "EUR": "€", "USD": "$"}
DEVISE_LABEL = {"MGA": "Ariary", "EUR": "Euro", "USD": "Dollar"}
METIER_LABEL = {
    "vannerie": "Vannerie",
    "couture": "Couture",
    "menuiserie": "Menuiserie",
    "broderie": "Broderie",
    "autre": "Autre",
}


def _fmt(valeur: float, devise: str) -> str:
    """Formate un montant selon la devise."""
    if devise == "MGA":
        entier = f"{round(valeur):,}".replace(",", " ")
        return f"{entier} Ar"
    symbole = DEVISE_SYMBOLE.get(devise, "")
    return f"{valeur:,.2f} {symbole}".replace(",", " ")


def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        return iso


def generer_devis_pdf(calcul: dict, artisan: str = "", client: str = "") -> bytes:
    """Génère un devis PDF à partir d'un calcul. Retourne les bytes du PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Devis - {calcul['nom_produit']}",
        author=artisan or "Artisan",
    )

    styles = getSampleStyleSheet()

    # Styles personnalisés
    titre = ParagraphStyle(
        "TitreDevis",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#14532d"),
        spaceAfter=4,
        alignment=0,
    )
    sous_titre = ParagraphStyle(
        "SousTitre",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#6b7280"),
        spaceAfter=14,
    )
    section = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#14532d"),
        spaceBefore=10,
        spaceAfter=6,
    )
    normal = styles["Normal"]
    small = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8.5,
        textColor=colors.HexColor("#6b7280"),
    )

    story = []

    # ---------- En-tête ----------
    story.append(Paragraph("DEVIS", titre))
    story.append(
        Paragraph(
            f"Émis le {_fmt_date(datetime.now().isoformat())} "
            f"— Référence n° {calcul['id']:05d}",
            sous_titre,
        )
    )

    # Bloc artisan / client
    artisan_txt = f"<b>Artisan</b><br/>{artisan or '—'}"
    client_txt = f"<b>Client</b><br/>{client or '—'}"
    entete_tbl = Table(
        [[Paragraph(artisan_txt, normal), Paragraph(client_txt, normal)]],
        colWidths=[85 * mm, 85 * mm],
    )
    entete_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(entete_tbl)
    story.append(Spacer(1, 6))

    # ---------- Détail du produit ----------
    story.append(Paragraph("Détail du produit", section))

    produit_tbl = Table(
        [
            ["Produit", calcul["nom_produit"]],
            ["Métier", METIER_LABEL.get(calcul["metier"], calcul["metier"])],
            ["Devise", f"{DEVISE_LABEL.get(calcul['devise'], calcul['devise'])} "
                       f"({DEVISE_SYMBOLE.get(calcul['devise'], '')})"],
        ],
        colWidths=[50 * mm, 120 * mm],
    )
    produit_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#374151")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(produit_tbl)
    story.append(Spacer(1, 8))

    # ---------- Décomposition du prix ----------
    story.append(Paragraph("Décomposition du prix", section))

    devise = calcul["devise"]
    main_oeuvre = calcul["temps_heures"] * calcul["taux_horaire"]
    marge_montant = calcul["prix_revient"] * (calcul["marge"] / 100)

    lignes = [
        ["Poste", "Détail", "Montant"],
        [
            "Matériaux",
            "",
            _fmt(calcul["cout_materiaux"], devise),
        ],
        [
            "Frais divers",
            "",
            _fmt(calcul["frais_divers"], devise),
        ],
        [
            "Main-d'œuvre",
            f"{calcul['temps_heures']} h × {_fmt(calcul['taux_horaire'], devise)}",
            _fmt(main_oeuvre, devise),
        ],
        [
            "Prix de revient",
            "",
            _fmt(calcul["prix_revient"], devise),
        ],
        [
            f"Marge ({calcul['marge']} %)",
            "",
            _fmt(marge_montant, devise),
        ],
        [
            "PRIX DE VENTE CONSEILLÉ",
            "",
            _fmt(calcul["prix_final"], devise),
        ],
    ]

    prix_tbl = Table(lignes, colWidths=[60 * mm, 65 * mm, 45 * mm])
    prix_tbl.setStyle(
        TableStyle(
            [
                # En-tête
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14532d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                # Ligne "Prix de revient" mise en valeur légère
                ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#f9fafb")),
                ("FONTNAME", (0, 4), (-1, 4), "Helvetica-Bold"),
                # Ligne finale prix de vente
                ("BACKGROUND", (0, 6), (-1, 6), colors.HexColor("#e8f5e9")),
                ("TEXTCOLOR", (0, 6), (-1, 6), colors.HexColor("#14532d")),
                ("FONTNAME", (0, 6), (-1, 6), "Helvetica-Bold"),
                ("FONTSIZE", (0, 6), (-1, 6), 11),
            ]
        )
    )
    story.append(prix_tbl)

    if devise == "MGA":
        story.append(Spacer(1, 4))
        story.append(
            Paragraph(
                "Montant arrondi au millier d'Ariary le plus proche.",
                small,
            )
        )

    # ---------- Conditions / mentions ----------
    story.append(Spacer(1, 14))
    story.append(Paragraph("Conditions", section))
    story.append(
        Paragraph(
            "Ce devis est valable 30 jours à compter de sa date d'émission. "
            "Le prix indiqué couvre les matériaux, les frais divers et la main-d'œuvre "
            "nécessaires à la réalisation du produit décrit. "
            "Toute modification de la commande pourra faire l'objet d'un nouveau devis.",
            normal,
        )
    )

    story.append(Spacer(1, 20))
    story.append(
        Paragraph(
            f"Devis généré le {_fmt_date(datetime.now().isoformat())} — "
            f"Référence {calcul['id']:05d}.",
            small,
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes