function chargerDemandes(){

fetch("http://127.0.0.1:5000/admin/demandes")

.then(res=>res.json())

.then(data=>{

let affichage="";


data.forEach(demande=>{

affichage += `
<p>
ID : ${demande[0]} <br>
Citoyen : ${demande[1]} <br>
Demande : ${demande[2]} <br>
Statut : ${demande[3]}
</p>
<hr>
`;

});


document.getElementById("liste").innerHTML = affichage;


});

}

function chargerDemandes(){

fetch("http://127.0.0.1:5000/admin/demandes")

.then(res => res.json())

.then(data => {

let affichage = "";

data.forEach(demande => {

affichage += `
<div>

<p>
ID : ${demande[0]}<br>
Citoyen : ${demande[1]}<br>
Type : ${demande[2]}<br>
Statut : ${demande[3]}
</p>

<button onclick="changerStatut(${demande[0]}, 'Acceptée')">
Accepter
</button>

<button onclick="changerStatut(${demande[0]}, 'Refusée')">
Refuser
</button>

<hr>

</div>
`;

});

document.getElementById("liste").innerHTML = affichage;

});

}

function changerStatut(id, statut){

fetch("http://127.0.0.1:5000/admin/modifier_statut", {

method: "POST",

headers: {
"Content-Type": "application/json"
},

body: JSON.stringify({
demande_id: id,
statut: statut
})

})

.then(res => res.json())

.then(data => {

alert(data.message);

chargerDemandes();

});

}