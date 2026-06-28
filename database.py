import sqlite3

# connexion à la base
connexion = sqlite3.connect("mairie.db")

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

curseur.execute("""
CREATE TABLE IF NOT EXISTS administrateurs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    email TEXT,
    mot_de_passe TEXT
)
""")

try:
    curseur.execute("ALTER TABLE demandes ADD COLUMN document TEXT")
except sqlite3.OperationalError:
    # La colonne existe déjà ou la table n'existe pas encore
    pass

connexion.commit()
connexion.close()

print("Base de données créée avec succès")

