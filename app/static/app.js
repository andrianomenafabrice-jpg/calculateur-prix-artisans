// ---------- Utilitaires ----------
const fmtAr = (n) =>
  new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(n) + " Ar";

// ---------- Soumission du formulaire ----------
const form = document.getElementById("form-calcul");
const resultatBox = document.getElementById("resultat");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    nom_produit: document.getElementById("nom_produit").value.trim(),
    cout_materiaux: parseFloat(document.getElementById("cout_materiaux").value),
    temps_heures: parseFloat(document.getElementById("temps_heures").value),
    taux_horaire: parseFloat(document.getElementById("taux_horaire").value),
    marge: parseFloat(document.getElementById("marge").value),
  };

  try {
    const res = await fetch("/api/calcul", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Erreur lors du calcul");
    }

    const data = await res.json();

    const prixRevient = data.cout_materiaux + data.temps_heures * data.taux_horaire;

    resultatBox.classList.remove("hidden");
    resultatBox.innerHTML = `
      <div><strong>${data.nom_produit}</strong></div>
      <div>Prix de revient : ${fmtAr(prixRevient)}</div>
      <div>Marge appliquée : ${data.marge}%</div>
      <div>Prix de vente conseillé : <strong>${fmtAr(data.prix_final)}</strong></div>
    `;

    form.reset();
    chargerHistorique();
  } catch (err) {
    alert("Erreur : " + err.message);
  }
});

// ---------- Historique ----------
const histBox = document.getElementById("historique");

async function chargerHistorique() {
  histBox.textContent = "Chargement…";
  try {
    const res = await fetch("/api/historique");
    if (!res.ok) throw new Error("Impossible de charger l'historique");
    const items = await res.json();

    if (items.length === 0) {
      histBox.innerHTML = "<em>Aucun calcul enregistré pour l'instant.</em>";
      return;
    }

    histBox.innerHTML = items
      .map(
        (it) => `
        <div class="item-hist">
          <div class="nom">${it.nom_produit}</div>
          <div>Prix conseillé : <span class="prix">${fmtAr(it.prix_final)}</span></div>
          <div class="date">${new Date(it.date_creation).toLocaleString("fr-FR")}</div>
        </div>
      `
      )
      .join("");
  } catch (err) {
    histBox.textContent = "Erreur : " + err.message;
  }
}

document.getElementById("btn-refresh").addEventListener("click", chargerHistorique);

// ---------- Chargement initial ----------
chargerHistorique();