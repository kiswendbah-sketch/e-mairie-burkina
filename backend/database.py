import sqlite3
import os

# connexion à la base
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
connexion = sqlite3.connect(os.path.join(BASE_DIR, "mairie.db"))

curseur = connexion.cursor()

# table des citoyens
curseur.execute("""
CREATE TABLE IF NOT EXISTS citoyens(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    email TEXT,
    mot_de_passe TEXT
)
""")

# table des demandes
curseur.execute("""
CREATE TABLE IF NOT EXISTS demandes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citoyen_id INTEGER,
    type_demande TEXT,
    statut TEXT,
    FOREIGN KEY(citoyen_id) REFERENCES citoyens(id)
)
""")


try:
    curseur.execute("ALTER TABLE demandes ADD COLUMN document TEXT")
except sqlite3.OperationalError:
    # La colonne existe déjà ou la table n'existe pas encore
    pass
# table des administrateurs
curseur.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    mot_de_passe TEXT
)
""")

curseur.execute("""
INSERT OR IGNORE INTO admin (username, mot_de_passe)
VALUES (?, ?)
""", ("admin", "admin123"))

connexion.commit()
connexion.close()

print("administrateur par défaut créé avec succès")

print("Base de données créée avec succès")