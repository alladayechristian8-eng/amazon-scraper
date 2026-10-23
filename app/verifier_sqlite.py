
import sqlite3
from pathlib import Path

base = Path(__file__).resolve().parent / "data" / "amazon.db"

print("Base utilisée :", base)

connexion = sqlite3.connect(str(base))
curseur = connexion.cursor()

try:
    curseur.execute("SELECT COUNT(*) FROM produits")
    print("Nombre de produits :", curseur.fetchone()[0])

    curseur.execute("""
        SELECT id, nom, prix
        FROM produits
        ORDER BY id DESC
        LIMIT 10
    """)

    for ligne in curseur.fetchall():
        print(ligne)

except sqlite3.Error as erreur:
    print("Erreur SQLite :", erreur)

finally:
    connexion.close()
