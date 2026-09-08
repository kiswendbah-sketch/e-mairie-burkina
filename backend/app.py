
from datetime import datetime
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

#Taille maximale d'un fichier : 5 Mo
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

bcrypt = Bcrypt(app)

def citoyen_connecte():
    return 'citoyen_id' in session

def admin_connecte():
    return 'admin' in session

@app.errorhandler(413)
def fichier_trop_volumineux(error):
    return jsonify({
        "message": "Fichier trop volumineux. La taille maximale autorisée est de 5 Mo."
    }), 413

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
        session['citoyen_id'] = row[0]
        return jsonify({'message': 'Connexion réussie', 'id': row[0]})

    return jsonify({'message': 'Email ou mot de passe incorrect'}), 401




@app.route('/uploads/<path:filename>')
def uploaded_file(filename):

    # Administrateur : accès à tous les documents
    if admin_connecte():
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename
        )

    # Citoyen non connecté
    if not citoyen_connecte():
        return redirect('/connexion')

    citoyen_id = session["citoyen_id"]

    db = get_db()
    c = db.cursor()

    # Vérifier que le document appartient bien au citoyen connecté
    c.execute("""
        SELECT id
        FROM demandes
        WHERE citoyen_id = ?
        AND (
            document = ?
            OR document_final = ?
        )
        LIMIT 1
    """, (citoyen_id, filename, filename))

    document = c.fetchone()

    db.close()

    # Document n'appartenant pas au citoyen
    if not document:
        return "Accès refusé à ce document", 403

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )


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
               demandes.document,
               demandes.date_demande
        FROM demandes
        JOIN citoyens ON demandes.citoyen_id = citoyens.id
    """)

    demandes = c.fetchall()

    db.close()

    return render_template("admin.html", demandes=demandes)

@app.route("/admin/demande/<int:id>")
def detail_demande(id):

    if not admin_connecte():
        return redirect("/admin/login")

    db = get_db()
    c = db.cursor()

    c.execute("""
    SELECT demandes.id,
           citoyens.nom,
           citoyens.email,
           demandes.type_demande,
           demandes.statut,
           demandes.document,
           demandes.date_demande,
           demandes.notification,
           demandes.document_final
    FROM demandes
    JOIN citoyens
    ON demandes.citoyen_id = citoyens.id
    WHERE demandes.id = ?
""", (id,))

    demande = c.fetchone()

    db.close()

    if not demande:
        return "Demande introuvable", 404

    return render_template(
        "detail_demande.html",
        demande=demande
    )

@app.route("/admin/supprimer/<int:id>", methods=["POST"])
def supprimer_demande(id):

    if not admin_connecte():
        return jsonify({
            "message": "Accès administrateur requis"
        }), 403

    db = get_db()
    c = db.cursor()

    # Récupérer les documents associés à la demande
    c.execute("""
        SELECT document, document_final
        FROM demandes
        WHERE id = ?
    """, (id,))

    demande = c.fetchone()

    if not demande:
        db.close()

        return jsonify({
            "message": "Demande introuvable"
        }), 404

    document = demande[0]
    document_final = demande[1]

    # Supprimer la demande de la base
    c.execute(
        "DELETE FROM demandes WHERE id = ?",
        (id,)
    )

    db.commit()
    db.close()

    # Supprimer le document envoyé
    if document:
        chemin_document = os.path.join(
            app.config["UPLOAD_FOLDER"],
            document
        )

        if os.path.exists(chemin_document):
            os.remove(chemin_document)

    # Supprimer le document officiel
    if document_final:
        chemin_document_final = os.path.join(
            app.config["UPLOAD_FOLDER"],
            document_final
        )

        if os.path.exists(chemin_document_final):
            os.remove(chemin_document_final)

    return jsonify({
        "message": "Demande et documents supprimés avec succès"
    })

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')

@app.route('/logout')
def logout():
    session.pop('citoyen_id', None)
    return redirect('/connexion')

@app.route('/admin/modifier_statut', methods=['POST'])
def modifier_statut():

    if not admin_connecte():
        return jsonify({
            "message": "Accès administrateur requis"
        }), 403

    data = request.get_json(silent=True) or {}

    demande_id = data.get("demande_id")
    statut = (data.get("statut") or "").strip()

    if not demande_id or not statut:
        return jsonify({
            "message": "Paramètres manquants"
        }), 400

    # Statuts autorisés uniquement
    statuts_autorises = {
        "En attente",
        "Acceptée",
        "Refusée"
    }

    if statut not in statuts_autorises:
        return jsonify({
            "message": "Statut invalide"
        }), 400

    # Notification correspondante
    if statut == "Acceptée":
        notification = "Votre demande a été acceptée."
    elif statut == "Refusée":
        notification = "Votre demande a été refusée."
    else:
        notification = "Votre demande est en attente de traitement."

    db = get_db()
    c = db.cursor()

    # Vérifier que la demande existe
    c.execute("""
        SELECT id
        FROM demandes
        WHERE id = ?
    """, (demande_id,))

    demande = c.fetchone()

    if not demande:
        db.close()
        return jsonify({
            "message": "Demande introuvable"
        }), 404

    # Modifier le statut et la notification
    c.execute("""
        UPDATE demandes
        SET statut = ?, notification = ?
        WHERE id = ?
    """, (
        statut,
        notification,
        demande_id
    ))

    db.commit()
    db.close()

    return jsonify({
        "message": "Statut mis à jour avec succès"
    })

@app.route("/demande_document", methods=["POST"])
def demande_document():

    if not citoyen_connecte():
        return jsonify({
            "message": "Vous devez être connecté"
        }), 401

    citoyen_id = session["citoyen_id"]
    type_demande = request.form.get("type_demande")
    fichier = request.files.get("document")

    if not type_demande or not fichier:
        return jsonify({
            "message": "Veuillez remplir tous les champs"
        }), 400

    # Sécuriser le nom du fichier
    filename = secure_filename(fichier.filename)

    if not filename:
        return jsonify({
            "message": "Nom de fichier invalide"
        }), 400

    # Extensions autorisées
    extensions_autorisees = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png"
    }

    extension = os.path.splitext(filename)[1].lower()

    if extension not in extensions_autorisees:
        return jsonify({
            "message": "Format de fichier non autorisé. Utilisez PDF, JPG ou PNG."
        }), 400

    # Éviter les conflits de noms
    nom_original = filename

    filename = (
        f"demande_{citoyen_id}_"
        f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_"
        f"{nom_original}"
    )

    chemin = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    # Enregistrer le fichier
    fichier.save(chemin)

    # Enregistrer la demande dans la base de données
    db = get_db()
    c = db.cursor()

    date_demande = datetime.now().strftime("%d/%m/%Y %H:%M")

    c.execute("""
        INSERT INTO demandes
        (citoyen_id, type_demande, statut, document, date_demande)
        VALUES (?, ?, ?, ?, ?)
    """, (
        citoyen_id,
        type_demande,
        "En attente",
        filename,
        date_demande
    ))

    db.commit()
    db.close()

    return jsonify({
        "message": "Demande envoyée avec succès"
    })

@app.route("/admin/citoyens")
def admin_citoyens():

    if not admin_connecte():
        return redirect("/admin/login")

    db = get_db()
    c = db.cursor()

    c.execute("""
        SELECT citoyens.id,
               citoyens.nom,
               citoyens.email,
               COUNT(demandes.id)
        FROM citoyens
        LEFT JOIN demandes
        ON demandes.citoyen_id = citoyens.id
        GROUP BY citoyens.id
        ORDER BY citoyens.id DESC
    """)

    citoyens = c.fetchall()

    db.close()

    return render_template("admin_citoyens.html", citoyens=citoyens)

@app.route("/admin/citoyen/<int:id>")
def detail_citoyen(id):
    
    if not admin_connecte():
        return redirect("/admin/login")

    db = get_db()
    c = db.cursor()

    c.execute("""
        SELECT id, nom, email
        FROM citoyens
        WHERE id = ?
    """, (id,))

    citoyen = c.fetchone()

    if not citoyen:
        return "Citoyen introuvable", 404

    c.execute("""
        SELECT id, type_demande, statut, document, notification, date_demande, document_final
        FROM demandes
        WHERE citoyen_id = ?
        ORDER BY id DESC
    """, (id,))

    demandes = c.fetchall()

    db.close()

    return render_template("detail_citoyen.html", citoyen=citoyen, demandes=demandes)

@app.route("/admin/citoyen/supprimer/<int:id>", methods=["POST"])
def supprimer_citoyen(id):

    if not admin_connecte():
        return jsonify({
            "message": "Accès administrateur requis"
        }), 403

    db = get_db()
    c = db.cursor()

    # Récupérer les documents du citoyen
    c.execute("""
        SELECT document, document_final
        FROM demandes
        WHERE citoyen_id = ?
    """, (id,))

    fichiers = c.fetchall()

    # Vérifier que le citoyen existe
    c.execute("""
        SELECT id
        FROM citoyens
        WHERE id = ?
    """, (id,))

    citoyen = c.fetchone()

    if not citoyen:
        db.close()
        return jsonify({
            "message": "Citoyen introuvable"
        }), 404

    # Supprimer les demandes
    c.execute("""
        DELETE FROM demandes
        WHERE citoyen_id = ?
    """, (id,))

    # Supprimer le citoyen
    c.execute("""
        DELETE FROM citoyens
        WHERE id = ?
    """, (id,))

    db.commit()
    db.close()

    # Supprimer les fichiers physiques
    for document, document_final in fichiers:

        if document:
            chemin = os.path.join(
                app.config["UPLOAD_FOLDER"],
                document
            )

            if os.path.exists(chemin):
                os.remove(chemin)

        if document_final:
            chemin_final = os.path.join(
                app.config["UPLOAD_FOLDER"],
                document_final
            )

            if os.path.exists(chemin_final):
                os.remove(chemin_final)

    return jsonify({
        "message": "Citoyen, demandes et documents supprimés avec succès"
    })

@app.route("/admin/deposer_document_final", methods=["POST"])
def deposer_document_final():

    if not admin_connecte():
        return jsonify({
            "message": "Accès administrateur requis"
        }), 403

    demande_id = request.form.get("demande_id")
    fichier = request.files.get("document_final")

    if not demande_id or not fichier:
        return jsonify({
            "message": "Demande ou fichier manquant"
        }), 400

    if not fichier.filename:
        return jsonify({
            "message": "Nom de fichier invalide"
        }), 400

    db = get_db()
    c = db.cursor()

    # Vérifier que la demande existe
    c.execute("""
        SELECT statut, document_final
        FROM demandes
        WHERE id = ?
    """, (demande_id,))

    demande = c.fetchone()

    if not demande:
        db.close()
        return jsonify({
            "message": "Demande introuvable"
        }), 404

    statut = demande[0]
    ancien_document_final = demande[1]

    # Le document officiel est disponible uniquement
    # pour une demande acceptée
    if statut != "Acceptée":
        db.close()
        return jsonify({
            "message": "Le document officiel ne peut être déposé que pour une demande acceptée."
        }), 400

    # Sécuriser le nom du fichier
    nom_original = secure_filename(fichier.filename)

    if not nom_original:
        db.close()
        return jsonify({
            "message": "Nom de fichier invalide"
        }), 400

    # Extensions autorisées
    extensions_autorisees = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png"
    }

    extension = os.path.splitext(nom_original)[1].lower()

    if extension not in extensions_autorisees:
        db.close()
        return jsonify({
            "message": "Format de fichier non autorisé. Utilisez PDF, JPG ou PNG."
        }), 400

    # Créer un nom unique
    filename = (
        f"final_{demande_id}_"
        f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_"
        f"{nom_original}"
    )

    chemin = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    # Enregistrer le nouveau document
    fichier.save(chemin)

    # Mettre à jour la base de données
    c.execute("""
        UPDATE demandes
        SET document_final = ?
        WHERE id = ?
    """, (filename, demande_id))

    db.commit()
    db.close()

    # Supprimer l'ancien document final s'il existe
    if ancien_document_final:
        ancien_chemin = os.path.join(
            app.config["UPLOAD_FOLDER"],
            ancien_document_final
        )

        if os.path.exists(ancien_chemin):
            os.remove(ancien_chemin)

    return jsonify({
        "message": "Document officiel déposé avec succès",
        "filename": filename
    })


@app.route("/admin/statistiques")
def statistiques():

    if not admin_connecte():
        return jsonify({"message": "Accès administrateur requis"}), 403

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

    if not citoyen_connecte():
        return redirect("/connexion")

    db = get_db()
    c = db.cursor()

    c.execute(" SELECT nom FROM citoyens WHERE id = ?", (session["citoyen_id"],))
    citoyen = c.fetchone()

    db.close()
    nom = citoyen[0] if citoyen else "Citoyen"
    
    return render_template("espace.html", nom=nom)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "GET":
        return render_template("admin_login.html")

    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    mot_de_passe = data.get("mot_de_passe") or ""

    if not username or not mot_de_passe:
        return jsonify({
            "message": "Veuillez remplir tous les champs"
        }), 400

    db = get_db()
    c = db.cursor()

    c.execute(
        "SELECT * FROM admin WHERE username=?",
        (username,)
    )

    admin = c.fetchone()

    db.close()

    if admin and bcrypt.check_password_hash(
        admin[2],
        mot_de_passe
    ):
        session["admin"] = username

        return jsonify({
            "message": "Connexion réussie"
        })

    return jsonify({
        "message": "Identifiants incorrects"
    }), 401

@app.route('/demande', methods=['POST', 'OPTIONS'])
def ajouter_demande():

    if request.method == 'OPTIONS':
        return '', 200

    # Vérifier la connexion du citoyen
    if not citoyen_connecte():
        return jsonify({
            'message': 'Vous devez être connecté'
        }), 401

    data = request.get_json(silent=True) or {}

    # L'identité vient de la session, pas du navigateur
    citoyen_id = session['citoyen_id']

    type_demande = (data.get('type_demande') or '').strip()

    if not type_demande:
        return jsonify({
            'message': 'Veuillez sélectionner un type de demande'
        }), 400

    db = get_db()
    c = db.cursor()

    c.execute("""
        INSERT INTO demandes
        (citoyen_id, type_demande, statut)
        VALUES (?, ?, ?)
    """, (
        citoyen_id,
        type_demande,
        'En attente'
    ))

    db.commit()
    db.close()

    return jsonify({
        'message': 'Demande envoyée avec succès'
    })

@app.route("/citoyen/statistiques")
def statistiques_citoyen():

    if "citoyen_id" not in session:
        return jsonify({"message": "Non connecté"}), 401

    db = get_db()
    c = db.cursor()

    citoyen_id = session["citoyen_id"]

    c.execute("SELECT COUNT(*) FROM demandes WHERE citoyen_id=?", (citoyen_id,))
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM demandes WHERE citoyen_id=? AND statut='En attente'", (citoyen_id,))
    attente = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM demandes WHERE citoyen_id=? AND statut='Acceptée'", (citoyen_id,))
    acceptees = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM demandes WHERE citoyen_id=? AND statut='Refusée'", (citoyen_id,))
    refusees = c.fetchone()[0]

    db.close()

    return jsonify({
        "total": total,
        "attente": attente,
        "acceptees": acceptees,
        "refusees": refusees
    })

@app.route("/citoyen/notifications")
def notifications_citoyen():

    if "citoyen_id" not in session:
        return jsonify([])

    db = get_db()
    c = db.cursor()

    c.execute("""
        SELECT notification
        FROM demandes
        WHERE citoyen_id = ?
        AND notification IS NOT NULL
        AND notification != ''
        ORDER BY id DESC
    """, (session["citoyen_id"],))

    notifications = [ligne[0] for ligne in c.fetchall()]

    db.close()

    return jsonify(notifications)

@app.route("/citoyen/dernieres_demandes")
def dernieres_demandes():

    if "citoyen_id" not in session:
        return jsonify([])

    db = get_db()
    c = db.cursor()

    c.execute("""
        SELECT type_demande, statut, notification
        FROM demandes
        WHERE citoyen_id = ?
        ORDER BY id DESC
        LIMIT 5
    """, (session["citoyen_id"],))

    demandes = c.fetchall()

    db.close()

    resultat = []

    for d in demandes:
        resultat.append({
            "type": d[0],
            "statut": d[1],
            "notification": d[2]
        })

    return jsonify(resultat)

@app.route("/mes_demandes")
def mes_demandes():

    if not citoyen_connecte():
        return redirect("/connexion")

    db = get_db()
    c = db.cursor()

    c.execute("""
        SELECT id,
               type_demande,
               statut,
               document,
               notification,
               date_demande,
               document_final
        FROM demandes
        WHERE citoyen_id = ?
        ORDER BY id DESC
    """, (session["citoyen_id"],))

    demandes = c.fetchall()

    db.close()

    return render_template(
        "mes_demandes.html",
        demandes=demandes
    )

@app.route('/test')
def test():
    return "SERVEUR E-MAIRIE"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

