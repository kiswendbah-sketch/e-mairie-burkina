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

