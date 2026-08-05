import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "mairie.db")

conn = sqlite3.connect(db_path)
c = conn.cursor()

try:
    c.execute("ALTER TABLE demandes ADD COLUMN notification TEXT DEFAULT ''")
    print("✅ Colonne notification ajoutée.")
except sqlite3.OperationalError as e:
    print("ℹ️", e)

conn.commit()
conn.close()