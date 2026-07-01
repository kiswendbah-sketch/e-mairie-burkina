function afficherMessage(id, message) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = message;
    }
}

function inscrire() {
    const nom = document.getElementById("nom")?.value.trim() || "";
    const email = document.getElementById("email")?.value.trim() || "";
    const motdepasse = document.getElementById("motdepasse")?.value.trim() || "";

    if (!nom || !email || !motdepasse) {
        afficherMessage("message", "Veuillez remplir tous les champs.");
        return;
    }

    fetch("http://e-mairie-burkina.onrender.com/inscription", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nom: nom,
            email: email,
            mot_de_passe: motdepasse
        })
    })
    .then(async response => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.message || "Erreur lors de l'inscription");
        }
        return data;
    })
    .then(data => {
        afficherMessage("message", data.message || "Citoyen enregistré");
    })
    .catch(error => {
        afficherMessage("message", error.message || "Impossible de joindre le serveur.");
    });
}

function login() {
    const email = document.getElementById("email")?.value.trim() || "";
    const password = document.getElementById("password")?.value.trim() || "";

    if (!email || !password) {
        afficherMessage("resultat", "Veuillez remplir tous les champs.");
        return;
    }

    fetch("http://e-mairie-burkina.onrender.com/connexion", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            mot_de_passe: password
        })
    })
    .then(async response => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.message || "Erreur de connexion");
        }
        return data;
    })
    .then(data => {
        afficherMessage("resultat", data.message || "Connexion réussie");

        if (data.id) {
            localStorage.setItem("citoyen_id", data.id);
            window.location.href = "espace.html";
        }
    })
    .catch(error => {
        afficherMessage("resultat", error.message || "Impossible de joindre le serveur.");
    });
}

function envoyerDemande() {
    const citoyen_id = localStorage.getItem("citoyen_id");
    const type = document.getElementById("demande")?.value || "";

    if (!citoyen_id) {
        afficherMessage("message", "Vous devez d'abord vous connecter.");
        return;
    }

    fetch("http://e-mairie-burkina.onrender.com/demande", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            citoyen_id: citoyen_id,
            type_demande: type
        })
    })
    .then(async response => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.message || "Erreur lors de l'envoi de la demande");
        }
        return data;
    })
    .then(data => {
        afficherMessage("message", data.message || "Demande envoyée avec succès");
    })
    .catch(error => {
        afficherMessage("message", error.message || "Impossible de joindre le serveur.");
    });
}