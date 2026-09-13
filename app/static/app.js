const DEVISE_LABEL = {
  MGA: "Ar",
  EUR: "€",
  USD: "$",
};

const METIER_LABEL = {
  vannerie: "Vannerie",
  couture: "Couture",
  menuiserie: "Menuiserie",
  broderie: "Broderie",
  autre: "Autre",
};

function formaterMontant(valeur, devise) {
  const symbole = DEVISE_LABEL[devise] || "";
  const n = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: devise === "MGA" ? 0 : 2,
  }).format(valeur);
  return devise === "MGA" ? `${n} ${symbole}` : `${n} ${symbole}`;
}

function formaterDate(iso) {
  try {
    return new Date(iso).toLocaleString("fr-FR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

// ---------- Formulaire ----------
const form = document.getElementById("form-calcul");
const errorBox = document.getElementById("form-error");
const resultatBox = document.getElementById("resultat");

function afficherErreur(msg) {
  errorBox.textContent = msg;
  errorBox.classList.remove("hidden");
}

function masquerErreur() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

// Chips pour la marge
document.querySelectorAll("#marge-hints .chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.getElementById("marge").value = chip.dataset.marge;
  });
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  masquerErreur();

  const payload = {
    nom_produit: form.nom_produit.value.trim(),
    metier: form.metier.value,
    devise: form.devise.value,
    cout_materiaux: parseFloat(form.cout_materiaux.value) || 0,
    frais_divers: parseFloat(form.frais_divers.value) || 0,
    temps_heures: parseFloat(form.temps_heures.value) || 0,
    taux_horaire: parseFloat(form.taux_horaire.value) || 0,
    marge: parseFloat(form.marge.value) || 0,
  };

  if (!payload.nom_produit) {
    return afficherErreur("Le nom du produit est obligatoire.");
  }

  try {
    const res = await fetch("/api/calcul", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Erreur lors du calcul.");
    }

    const data = await res.json();
    afficherResultat(data);
    form.reset();
    chargerHistorique();
  } catch (err) {
    afficherErreur(err.message);
  }
});

function afficherResultat(data) {
  const devise = data.devise;
  resultatBox.classList.remove("hidden");
  resultatBox.innerHTML = `
    <h3>Résultat pour « ${escapeHtml(data.nom_produit)} »</h3>
    <div class="ligne"><span>Coût des matériaux</span><span>${formaterMontant(data.cout_materiaux, devise)}</span></div>
    <div class="ligne"><span>Frais divers</span><span>${formaterMontant(data.frais_divers, devise)}</span></div>
    <div class="ligne"><span>Main-d'œuvre (${data.temps_heures} h × ${formaterMontant(data.taux_horaire, devise)})</span><span>${formaterMontant(data.temps_heures * data.taux_horaire, devise)}</span></div>
    <div class="ligne"><span>Prix de revient</span><span>${formaterMontant(data.prix_revient, devise)}</span></div>
    <div class="ligne"><span>Marge appliquée</span><span>${data.marge} %</span></div>
    <div class="total"><span>Prix de vente conseillé</span><strong>${formaterMontant(data.prix_final, devise)}</strong></div>
    <div class="meta">Métier : ${METIER_LABEL[data.metier] || data.metier}${devise === "MGA" ? " · arrondi au millier d'Ariary" : ""}</div>
  `;
}

// ---------- Historique ----------
const histBox = document.getElementById("historique");

async function chargerHistorique() {
  histBox.innerHTML = '<div class="empty">Chargement…</div>';
  try {
    const res = await fetch("/api/historique");
    if (!res.ok) throw new Error("Impossible de charger l'historique.");
    const items = await res.json();

    if (!items.length) {
      histBox.innerHTML = '<div class="empty">Aucun calcul enregistré pour l\'instant.</div>';
      return;
    }

    histBox.innerHTML = items.map(rendreItem).join("");
  } catch (err) {
    histBox.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
  }
}

function rendreItem(it) {
  const devise = it.devise;
  return `
    <div class="item-hist">
      <div class="head">
        <span class="nom" title="${escapeHtml(it.nom_produit)}">${escapeHtml(it.nom_produit)}</span>
        <span class="prix">${formaterMontant(it.prix_final, devise)}</span>
      </div>
      <div class="details">
        <span class="badge">${METIER_LABEL[it.metier] || it.metier}</span>
        <span>${it.temps_heures} h × ${formaterMontant(it.taux_horaire, devise)}</span>
        <span>marge ${it.marge} %</span>
      </div>
      <div class="date">${formaterDate(it.date_creation)}</div>
    </div>
  `;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

document.getElementById("btn-refresh").addEventListener("click", chargerHistorique);

chargerHistorique();