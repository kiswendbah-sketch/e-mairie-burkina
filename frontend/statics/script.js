function afficherMessage(id, message) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = message;
    }
}


function login() {
    const email = document.getElementById("email")?.value.trim() || "";
    const password = document.getElementById("password")?.value.trim() || "";

    if (!email || !password) {
        afficherMessage("resultat", "Veuillez remplir tous les champs.");
        return;
    }

    fetch("/connexion", {
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
            window.location.href = "espace";
        }
    })
    .catch(error => {
        afficherMessage("resultat", error.message || "Impossible de joindre le serveur.");
    });
}

document.getElementById("demandeForm")?.addEventListener("submit", function(e){

    e.preventDefault();

    const formData = new FormData();

    formData.append("citoyen_id", localStorage.getItem("citoyen_id"));
    formData.append("type_demande", document.getElementById("demande").value);
    formData.append("document", document.getElementById("document").files[0]);

    fetch("/demande_document", {
        method: "POST",
        body: formData
    })

    .then(response => response.json())

    .then(data => {
        document.getElementById("message").textContent = data.message;
    })

    .catch(error => {
        console.log(error);
        document.getElementById("message").textContent = "Erreur lors de l'envoi.";
    });

});

document.getElementById("registerForm")?.addEventListener("submit", function(e){

    e.preventDefault();

    let nom = document.getElementById("nom").value;
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;


    fetch("/inscription", {

        method: "POST",

        headers:{
            "Content-Type":"application/json"
        },

        body: JSON.stringify({
            nom: nom,
            email: email,
            mot_de_passe: password
        })

    })

    .then(response => response.json())

    .then(data => {

        alert(data.message);

    })

    .catch(error => {

        console.log(error);

        alert("Erreur de connexion");

    });

});

document.getElementById("loginForm")?.addEventListener("submit", function(e){

    e.preventDefault();
    console.log("connexion envoyée");

    fetch("/connexion", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: document.getElementById("email").value,
            mot_de_passe: document.getElementById("password").value
        })
    })

    .then(response => response.json())

    .then(data => {

        alert(data.message);

        if(data.id){
            localStorage.setItem("citoyen_id", data.id);
            window.location.href = "/espace";
        }

    })

    .catch(error => {

        console.log(error);
        alert("Erreur de connexion");

    });

});

document.addEventListener("DOMContentLoaded", function () {

    const tableau = document.getElementById("listeDemandes");

    if (!tableau) return;

    const citoyen_id = localStorage.getItem("citoyen_id");

    if (!citoyen_id) {
        tableau.innerHTML = "<tr><td colspan='4'>Vous n'êtes pas connecté.</td></tr>";
        return;
    }

    fetch("/mes_demandes/" + citoyen_id)
        .then(response => response.json())
        .then(demandes => {

            tableau.innerHTML = "";

            demandes.forEach(demande => {

                tableau.innerHTML += `
                    <tr>
                        <td>${demande[0]}</td>
                        <td>${demande[1]}</td>
                        <td>${demande[2]}</td>
                        <td>${demande[3] || "Aucun document"}</td>
                    </tr>
                `;

            });

        })
        .catch(error => {
            console.log(error);
            tableau.innerHTML = "<tr><td colspan='4'>Erreur de chargement.</td></tr>";
        });

});