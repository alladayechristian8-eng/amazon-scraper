
import sqlite3
from pathlib import Path


RACINE_PROJET = Path(__file__).resolve().parents[2]
DOSSIER_DATA = RACINE_PROJET / "data"
CHEMIN_BASE = DOSSIER_DATA / "amazon.db"


class Database:
    def __init__(self):
        DOSSIER_DATA.mkdir(parents=True, exist_ok=True)

        self.connexion = sqlite3.connect(str(CHEMIN_BASE))
        self.curseur = self.connexion.cursor()

        self.curseur.execute("""
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categorie TEXT,
                recherche TEXT,
                nom TEXT NOT NULL,
                prix TEXT,
                note TEXT,
                nombre_avis TEXT,
                image TEXT,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Ajouter les colonnes manquantes si la table existe déjà.
        self.curseur.execute("PRAGMA table_info(produits)")
        colonnes_existantes = {
            colonne[1] for colonne in self.curseur.fetchall()
        }

        colonnes_a_ajouter = {
            "categorie": "TEXT",
            "recherche": "TEXT",
            "nom": "TEXT",
            "prix": "TEXT",
            "note": "TEXT",
            "nombre_avis": "TEXT",
            "image": "TEXT",
            "date_ajout": "TIMESTAMP"
        }

        for nom_colonne, type_colonne in colonnes_a_ajouter.items():
            if nom_colonne not in colonnes_existantes:
                self.curseur.execute(
                    f"ALTER TABLE produits ADD COLUMN "
                    f"{nom_colonne} {type_colonne}"
                )

        self.connexion.commit()

        print(f"Base SQLite connectée : {CHEMIN_BASE}")

    def ajouter_produit(self, produit, categorie, recherche):
        self.curseur.execute("""
            INSERT INTO produits (
                categorie,
                recherche,
                nom,
                prix,
                note,
                nombre_avis,
                image
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            categorie or "Recherche libre",
            recherche,
            produit.nom,
            produit.prix,
            produit.note,
            produit.nombre_avis,
            produit.image
        ))

    def compter_produits(self):
        self.curseur.execute(
            "SELECT COUNT(*) FROM produits"
        )
        return self.curseur.fetchone()[0]

    def obtenir_produits(self, limite=10):
        self.curseur.execute("""
            SELECT id, categorie, recherche, nom,
                   prix, note, nombre_avis, image
            FROM produits
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))

        return self.curseur.fetchall()

    def fermer(self):
        if self.connexion:
            self.connexion.commit()
            self.connexion.close()
            self.connexion = None
            print("Connexion SQLite fermée.")
