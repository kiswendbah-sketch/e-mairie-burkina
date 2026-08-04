
from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import sqlite3
import os
from werkzeug.utils import secure_filename
import database

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'frontend', 'templates')
STATICS_DIR = os.path.join(BASE_DIR, 'frontend', 'statics')

app = Flask(__name__, static_folder=STATICS_DIR, template_folder=TEMPLATES_DIR)
app.secret_key = "e-Mairie-Burkina-2026"

CORS(app)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

bcrypt = Bcrypt(app)

#database.creer_administrateur()

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route('/')
def accueil():
    return render_template("mairie.html")


def get_db():
    chemin = os.path.join(BASE_DIR, 'mairie.db')
    print(chemin)
    return sqlite3.connect(chemin)


@app.route('/inscription', methods=['GET', 'POST', 'OPTIONS'])
def inscription():
    if request.method == 'GET':
        return render_template("inscription.html")
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json(silent=True) or {}
    nom = data.get('nom', '').strip()
    email = data.get('email', '').strip()
    mot_de_passe = data.get('mot_de_passe', '').strip()

    if not nom or not email or not mot_de_passe:
        return jsonify({'message': 'Veuillez remplir tous les champs'}), 400

    mot_de_passe_hash = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

    db = get_db()
    c = db.cursor()
    c.execute('INSERT INTO citoyens (nom,email,mot_de_passe) VALUES (?,?,?)', (nom, email, mot_de_passe_hash))
    db.commit()
    db.close()

    return jsonify({'message': 'Citoyen enregistré'})


@app.route('/connexion', methods=['GET', 'POST', 'OPTIONS'])
def connexion():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip()
    mot_de_passe = (data.get('mot_de_passe') or '').strip()

    if not email or not mot_de_passe:
        return jsonify({'message': 'Veuillez remplir tous les champs'}), 400

    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM citoyens WHERE email=?', (email,))
    row = c.fetchone()
    db.close()

    if row and bcrypt.check_password_hash(row[3], mot_de_passe):
        return jsonify({'message': 'Connexion réussie', 'id': row[0]})

    return jsonify({'message': 'Email ou mot de passe incorrect'}), 401


@app.route('/demande', methods=['POST', 'OPTIONS'])
def ajouter_demande():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json(silent=True) or {}
    citoyen_id = data.get('citoyen_id')
    type_demande = (data.get('type_demande') or '').strip()


    if not citoyen_id or not type_demande:
        return jsonify({'message': 'Veuillez remplir tous les champs'}), 400

    db = get_db()
    c = db.cursor()
    c.execute('INSERT INTO demandes (citoyen_id, type_demande, statut) VALUES (?,?,?)', (citoyen_id, type_demande, 'En attente'))
    db.commit()
    db.close()

    return jsonify({'message': 'Demande envoyée avec succès'})


@app.route('/upload', methods=['POST'])
def upload():
    # accept file and demande_id
    if 'file' not in request.files:
        return jsonify({'message': 'Aucun fichier envoyé'}), 400
    file = request.files['file']
    demande_id = request.form.get('demande_id')
    if file.filename == '':
        return jsonify({'message': 'Nom de fichier invalide'}), 400

    filename = secure_filename(file.filename)
    dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(dest)

    if demande_id:
        db = get_db()
        c = db.cursor()
        c.execute('UPDATE demandes SET document = ? WHERE id = ?', (filename, demande_id))
        db.commit()
        db.close()

    return jsonify({'message': 'Fichier envoyé', 'filename': filename})


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/admin/demandes')
def voir_demandes():
    if 'admin' not in session:
        return redirect('/admin/login')

    db = get_db()
    c = db.cursor()

    c.execute("""
        SELECT demandes.id,
               citoyens.nom,
               demandes.type_demande,
               demandes.statut,
               demandes.document
        FROM demandes
        JOIN citoyens ON demandes.citoyen_id = citoyens.id
    """)

    demandes = c.fetchall()

    print(demandes)   # <-- ajoute cette ligne

    db.close()

    return render_template("admin.html", demandes=demandes)

@app.route("/admin/supprimer/<int:id>", methods=["POST"])
def supprimer_demande(id):
    db = get_db()
    c = db.cursor()

    c.execute("DELETE FROM demandes WHERE id = ?", (id,))

    db.commit()
    db.close()

    return jsonify({"message": "Demande supprimée avec succès"})

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')


@app.route('/admin/modifier_statut', methods=['POST'])
def modifier_statut():
    data = request.get_json(silent=True) or {}
    demande_id = data.get('demande_id')
    statut = data.get('statut')
    
    db = get_db()
    c = db.cursor()

    c.execute("UPDATE demandes SET statut = ? WHERE id = ?", (statut, demande_id))
    db.commit()
    db.close()

    return jsonify({'message': 'Statut mis à jour'})

    if not demande_id or statut is None:
        return jsonify({'message': 'Paramètres manquants'}), 400

    db = get_db()
    c = db.cursor()
    c.execute('UPDATE demandes SET statut = ? WHERE id = ?', (statut, demande_id))
    db.commit()
    db.close()

    return jsonify({'message': 'Statut mis à jour'})

@app.route("/demande_document", methods=["POST"])
def demande_document():

    citoyen_id = request.form.get("citoyen_id")
    type_demande = request.form.get("type_demande")
    fichier = request.files.get("document")

    print("citoyen_id =", citoyen_id)
    print("type_demande =", type_demande)
    print("fichier =", fichier)

    if not citoyen_id or not type_demande or not fichier:
        return jsonify({"message": "Veuillez remplir tous les champs"}), 400

    filename = secure_filename(fichier.filename)
    fichier.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    db = get_db()
    c = db.cursor()

    c.execute("""
        INSERT INTO demandes (citoyen_id, type_demande, statut, document)
        VALUES (?, ?, ?, ?)
    """, (citoyen_id, type_demande, "En attente", filename))

    db.commit()
    db.close()

    return jsonify({"message": "Demande envoyée avec succès"})


@app.route("/admin/statistiques")
def statistiques():

    db = get_db()
    curseur = db.cursor()

    curseur.execute(
        "SELECT COUNT(*) FROM demandes"
    )
    total = curseur.fetchone()[0]


    curseur.execute(
        "SELECT COUNT(*) FROM demandes WHERE statut='En attente'"
    )
    attente = curseur.fetchone()[0]


    curseur.execute(
        "SELECT COUNT(*) FROM demandes WHERE statut='Acceptée'"
    )
    acceptees = curseur.fetchone()[0]


    curseur.execute(
        "SELECT COUNT(*) FROM demandes WHERE statut='Refusée'"
    )
    refusees = curseur.fetchone()[0]


    db.close()


    return jsonify({
        "total": total,
        "en_attente": attente,
        "acceptees": acceptees,
        "refusees": refusees
    })

@app.route("/espace")
def espace():
    return render_template("espace.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")

    data = request.get_json()

    username = data["username"]
    mot_de_passe = data["mot_de_passe"]

    db = get_db()
    c = db.cursor()

    c.execute("SELECT * FROM admin WHERE username=?", (username,))
    admin = c.fetchone()
    db.close()

    if admin and admin[2] == mot_de_passe:
        session["admin"] = username
        return jsonify({"message": "Connexion réussie"})

    return jsonify({"message": "Identifiants incorrects"}), 401

@app.route("/mes_demandes/<int:citoyen_id>")
def mes_demandes(citoyen_id):

    db = get_db()
    c = db.cursor()

    c.execute("""
        SELECT id, type_demande, statut, document
        FROM demandes
        WHERE citoyen_id = ?
    """, (citoyen_id,))

    demandes = c.fetchall()
    db.close()

    return jsonify(demandes)

@app.route("/mes_demandes")
def page_mes_demandes():
    return render_template("mes_demandes.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

