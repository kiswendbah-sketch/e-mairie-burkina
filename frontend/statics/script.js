/* =========================
   FONCTION UTILITAIRE
========================= */

function afficherMessage(id, message) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = message;
    }
}


/* =========================
   CONNEXION CITOYEN
========================= */

function initialiserConnexion() {

    const loginForm = document.getElementById("loginForm");

    if (!loginForm) {
        return;
    }

    loginForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        if (!email || !password) {
            alert("Veuillez remplir tous les champs.");
            return;
        }

        try {

            const response = await fetch("/connexion", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    mot_de_passe: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || "Erreur de connexion"
                );
            }

            alert(data.message);

            if (data.id) {

                localStorage.setItem(
                    "citoyen_id",
                    data.id
                );

                window.location.href = "/espace";
            }

        } catch (error) {

            console.error("Erreur connexion :", error);

            alert(error.message);
        }

    });
}


/* =========================
   INSCRIPTION CITOYEN
========================= */

function initialiserInscription() {

    const registerForm =
        document.getElementById("registerForm");

    if (!registerForm) {
        return;
    }

    registerForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const nom =
            document.getElementById("nom").value.trim();

        const email =
            document.getElementById("email").value.trim();

        const password =
            document.getElementById("password").value.trim();

        if (!nom || !email || !password) {

            alert("Veuillez remplir tous les champs.");

            return;
        }

        try {

            const response = await fetch("/inscription", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    nom: nom,
                    email: email,
                    mot_de_passe: password
                })

            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || "Erreur lors de l'inscription."
                );
            }

            alert(data.message);

            if (data.message === "Citoyen enregistré") {
                window.location.href = "/connexion";
            }

        } catch (error) {

            console.error("Erreur inscription :", error);

            alert(error.message);
        }

    });
}


/* =========================
   ENVOI D'UNE DEMANDE
========================= */

function initialiserDemande() {

    const demandeForm =
        document.getElementById("demandeForm");

    if (!demandeForm) {
        return;
    }

    demandeForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const typeDemande =
            document.getElementById("demande").value;

        const fichierInput =
            document.getElementById("document");

        const fichier =
            fichierInput.files[0];

        if (!fichier) {

            afficherMessage(
                "message",
                "Veuillez sélectionner un document."
            );

            return;
        }

        const formData = new FormData();

        formData.append(
            "type_demande",
            typeDemande
        );

        formData.append(
            "document",
            fichier
        );

        try {

            const response = await fetch(
                "/demande_document",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message ||
                    "Erreur lors de l'envoi."
                );
            }

            afficherMessage(
                "message",
                data.message
            );

            demandeForm.reset();

            chargerStatistiques();
            chargerNotifications();
            chargerDernieresDemandes();

        } catch (error) {

            console.error("Erreur demande :", error);

            afficherMessage(
                "message",
                error.message
            );
        }

    });
}


/* =========================
   STATISTIQUES CITOYEN
========================= */

async function chargerStatistiques() {

    const total =
        document.getElementById("total");

    if (!total) {
        return;
    }

    try {

        const response =
            await fetch("/citoyen/statistiques");

        const data =
            await response.json();

        if (!response.ok || data.message) {
            return;
        }

        document.getElementById("total").innerText =
            data.total;

        document.getElementById("attente").innerText =
            data.attente;

        document.getElementById("acceptees").innerText =
            data.acceptees;

        document.getElementById("refusees").innerText =
            data.refusees;

    } catch (error) {

        console.error(
            "Erreur statistiques :",
            error
        );
    }
}


/* =========================
   NOTIFICATIONS
========================= */

async function chargerNotifications() {

    const liste =
        document.getElementById("liste_notifications");

    if (!liste) {
        return;
    }

    try {

        const response =
            await fetch("/citoyen/notifications");

        const data =
            await response.json();

        liste.innerHTML = "";

        if (!data || data.length === 0) {

            liste.innerHTML =
                "<li>Aucune notification.</li>";

            return;
        }

        data.forEach(notification => {

            const li =
                document.createElement("li");

            li.textContent =
                notification;

            liste.appendChild(li);

        });

    } catch (error) {

        console.error(
            "Erreur notifications :",
            error
        );
    }
}


/* =========================
   DERNIÈRES DEMANDES
========================= */

async function chargerDernieresDemandes() {

    const tableau =
        document.getElementById("listeDemandes");

    if (!tableau) {
        return;
    }

    try {

        const response =
            await fetch("/citoyen/dernieres_demandes");

        const data =
            await response.json();

        tableau.innerHTML = "";

        if (!data || data.length === 0) {

            tableau.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center">
                        Aucune demande.
                    </td>
                </tr>
            `;

            return;
        }

        data.forEach(demande => {

            const ligne =
                document.createElement("tr");

            const type =
                document.createElement("td");

            const statut =
                document.createElement("td");

            const notification =
                document.createElement("td");

            type.textContent =
                demande.type;

            statut.textContent =
                demande.statut;

            notification.textContent =
                demande.notification || "";

            ligne.appendChild(type);
            ligne.appendChild(statut);
            ligne.appendChild(notification);

            tableau.appendChild(ligne);

        });

    } catch (error) {

        console.error(
            "Erreur dernières demandes :",
            error
        );
    }
}


/* =========================
   INITIALISATION
========================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initialiserConnexion();

        initialiserInscription();

        initialiserDemande();

        if (
            window.location.pathname === "/espace"
        ) {

            chargerStatistiques();

            chargerNotifications();

            chargerDernieresDemandes();
        }

    }
);