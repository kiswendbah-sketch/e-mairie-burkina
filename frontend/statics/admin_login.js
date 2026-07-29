async function connexionAdmin() {

    let username = document.getElementById("username").value;
    let mot_de_passe = document.getElementById("mot_de_passe").value;

    let reponse = await fetch("/admin/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            mot_de_passe: mot_de_passe
        })
    });

    let resultat = await reponse.json();

    if (reponse.ok) {
        window.location = "/admin/demandes";
    } else {
        document.getElementById("msg").innerText = resultat.message;
    }
}