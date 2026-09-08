from flask_bcrypt import Bcrypt
import sqlite3
import os

bcrypt = Bcrypt()

# Mot de passe administrateur
mot_de_passe_admin = bcrypt.generate_password_hash(
    "admin123"
).decode("utf-8")

# Connexion à la base
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
connexion = sqlite3.connect(
    os.path.join(BASE_DIR, "mairie.db")
)

curseur = connexion.cursor()

# =========================
# TABLE CITOYENS
# =========================

curseur.execute("""
CREATE TABLE IF NOT EXISTS citoyens(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    email TEXT,
    mot_de_passe TEXT
)
""")

# =========================
# TABLE DEMANDES
# =========================

curseur.execute("""
CREATE TABLE IF NOT EXISTS demandes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citoyen_id INTEGER,
    type_demande TEXT,
    statut TEXT,
    FOREIGN KEY(citoyen_id) REFERENCES citoyens(id)
)
""")

# Ajouter les colonnes si elles n'existent pas

try:
    curseur.execute(
        "ALTER TABLE demandes ADD COLUMN document TEXT"
    )
except sqlite3.OperationalError:
    pass

try:
    curseur.execute(
        "ALTER TABLE demandes ADD COLUMN notification TEXT"
    )
except sqlite3.OperationalError:
    pass

try:
    curseur.execute(
        "ALTER TABLE demandes ADD COLUMN date_demande TEXT"
    )
except sqlite3.OperationalError:
    pass

try:
    curseur.execute(
        "ALTER TABLE demandes ADD COLUMN document_final TEXT")
except sqlite3.OperationalError:
        pass


# =========================
# TABLE ADMINISTRATEURS
# =========================

curseur.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    mot_de_passe TEXT
)
""")

# Vérifier si admin existe
curseur.execute(
    "SELECT id, mot_de_passe FROM admin WHERE username = ?",
    ("admin",)
)

admin_existant = curseur.fetchone()

if admin_existant is None:

    curseur.execute(
        "INSERT INTO admin (username, mot_de_passe) VALUES (?, ?)",
        ("admin", mot_de_passe_admin)
    )

elif admin_existant[1] == "admin123":

    curseur.execute(
        "UPDATE admin SET mot_de_passe = ? WHERE username = ?",
        (mot_de_passe_admin, "admin")
    )

connexion.commit()
connexion.close()

print("Administrateur par défaut créé avec succès")
print("Base de données créée avec succès")