fetch("http://127.0.0.1:5000/admin/statistiques")


.then(res=>res.json())


.then(data=>{


document.getElementById("stats").innerHTML = `

Total demandes : ${data.total}

<br>

En attente : ${data.en_attente}

<br>

Acceptées : ${data.acceptees}

<br>

Refusées : ${data.refusees}

`;


});