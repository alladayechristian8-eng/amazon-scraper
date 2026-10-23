
import csv
import os
import re
import unicodedata
import requests

from app.scraper.amazon_scraper import AmazonScraper
from app.models.database import Database


CATEGORIES = [
    "Téléphones portables et accessoires",
    "Informatique",
    "Audio et vidéo portable",
    "TV, vidéo et home cinéma",
    "Photo et caméscopes",
    "Tablettes PC et liseuses",
    "Réseaux et connectivité",
    "GPS et accessoires",
    "Piles et chargeurs",
    "Électronique embarquée",
    "Radios et accessoires",
    "Univers Hi-Fi"
]

DOSSIER_DATA = "data"

COLONNES = [
    "categorie",
    "recherche",
    "nom",
    "prix",
    "note",
    "nombre_avis",
    "image"
]


def nom_dossier(texte):
    texte = unicodedata.normalize("NFKD", texte)
    texte = texte.encode("ascii", "ignore").decode("ascii")
    texte = texte.lower()
    texte = re.sub(r"[^a-z0-9]+", "_", texte)
    return texte.strip("_") or "recherche"


def telecharger_image(url, dossier, numero):
    if not url:
        return ""

    try:
        os.makedirs(dossier, exist_ok=True)

        reponse = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        reponse.raise_for_status()

        type_image = reponse.headers.get(
            "Content-Type", ""
        ).lower()

        if "png" in type_image:
            extension = ".png"
        elif "webp" in type_image:
            extension = ".webp"
        else:
            extension = ".jpg"

        chemin = os.path.join(
            dossier,
            f"image_{numero}{extension}"
        )

        with open(chemin, "wb") as fichier:
            fichier.write(reponse.content)

        return chemin.replace("\\", "/")

    except requests.RequestException as erreur:
        print(f"Image {numero} non téléchargée : {erreur}")
        return ""


def enregistrer_csv(chemin, lignes):
    dossier = os.path.dirname(chemin)

    if dossier:
        os.makedirs(dossier, exist_ok=True)

    with open(
        chemin,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as fichier:
        writer = csv.writer(fichier, delimiter=";")
        writer.writerow(COLONNES)
        writer.writerows(lignes)

    print(f"Fichier enregistré : {chemin}")


def enregistrer_recap(lignes):
    os.makedirs(DOSSIER_DATA, exist_ok=True)

    chemin = os.path.join(DOSSIER_DATA, "recap.csv")

    with open(
        chemin,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as fichier:
        writer = csv.writer(fichier, delimiter=";")
        writer.writerow(COLONNES)
        writer.writerows(lignes)

    print(f"\nRécapitulatif enregistré : {chemin}")


def traiter_recherche(categorie, recherche, nombre_pages):
    dossier_categorie = nom_dossier(
        categorie or "recherche_libre"
    )
    dossier_produit = nom_dossier(recherche)

    dossier = os.path.join(
        DOSSIER_DATA,
        dossier_categorie,
        dossier_produit
    )

    dossier_images = os.path.join(dossier, "Images")
    os.makedirs(dossier_images, exist_ok=True)

    scraper = None
    db = None
    lignes = []

    try:
        print("\n" + "=" * 55)
        print(f"Catégorie : {categorie or 'Recherche libre'}")
        print(f"Produit recherché : {recherche}")
        print("=" * 55)

        # 1. Scraper les produits
        scraper = AmazonScraper()

        produits = scraper.rechercher(
            recherche=recherche,
            categorie=categorie,
            nombre_pages=nombre_pages
        )

        print(f"\nProduits trouvés par le scraper : {len(produits)}")

        # 2. Préparer les lignes et télécharger les images
        for numero, produit in enumerate(produits, start=1):
            chemin_image = telecharger_image(
                produit.image,
                dossier_images,
                numero
            )

            if chemin_image:
                produit.image = chemin_image

            lignes.append([
                categorie or "Recherche libre",
                recherche,
                produit.nom,
                produit.prix,
                produit.note,
                produit.nombre_avis,
                produit.image
            ])

        # 3. Enregistrer dans SQLite
        db = Database()

        for produit in produits:
            db.ajouter_produit(
                produit,
                categorie,
                recherche
            )

        # Valider les insertions avant de vérifier le total.
        db.connexion.commit()

        print(
            "\nNombre total de produits dans SQLite :",
            db.compter_produits()
        )

        # 4. Enregistrer également dans le CSV
        chemin_csv = os.path.join(dossier, "data.csv")
        enregistrer_csv(chemin_csv, lignes)

        print(f"\nNombre de produits trouvés : {len(produits)}")
        print(f"Dossier des résultats : {dossier}")

    except Exception as erreur:
        print(f"\nErreur pendant le traitement : {erreur}")

        if db is not None and db.connexion is not None:
            db.connexion.rollback()

    finally:
        if db is not None:
            try:
                db.fermer()
            except Exception as erreur:
                print(f"Erreur lors de la fermeture SQLite : {erreur}")

        if scraper is not None:
            try:
                scraper.fermer()
            except Exception as erreur:
                print(f"Erreur lors de la fermeture du scraper : {erreur}")

    return lignes


def demander_pages():
    while True:
        saisie = input(
            "Nombre de pages à scraper (défaut : 3) : "
        ).strip()

        if not saisie:
            return 3

        if saisie.isdigit() and int(saisie) > 0:
            return int(saisie)

        print("Entre un nombre entier supérieur à zéro.")


def afficher_menu():
    while True:
        print("\n========== AMAZON HIGH-TECH ==========")
        print("1. Choisir une sous-catégorie et un produit")
        print("2. Rechercher un produit sans choisir de catégorie")
        print("3. Scraper plusieurs sous-catégories")
        print("4. Quitter")
        print("======================================")

        choix = input("Ton choix : ").strip()

        if choix == "4":
            print("Au revoir !")
            break

        if choix == "1":
            print("\n--- CHOISIS UNE SOUS-CATÉGORIE ---")

            for numero, nom in enumerate(CATEGORIES, start=1):
                print(f"{numero}. {nom}")

            selection = input(
                "\nNuméro de la sous-catégorie : "
            ).strip()

            if (
                not selection.isdigit()
                or not 1 <= int(selection) <= len(CATEGORIES)
            ):
                print("Choix invalide.")
                continue

            categorie = CATEGORIES[int(selection) - 1]

            print(f"\nSous-catégorie choisie : {categorie}")

            recherche = input(
                "Nom du produit à rechercher : "
            ).strip()

            if not recherche:
                print("Le nom du produit ne peut pas être vide.")
                continue

            recherches = [(categorie, recherche)]

        elif choix == "2":
            recherche = input(
                "\nNom du produit à rechercher : "
            ).strip()

            if not recherche:
                print("Le nom du produit ne peut pas être vide.")
                continue

            recherches = [("", recherche)]

        elif choix == "3":
            print(
                "\nSaisis un produit pour chaque sous-catégorie. "
                "Appuie sur Entrée pour ignorer une catégorie."
            )

            recherches = []

            for nom_categorie in CATEGORIES:
                print(f"\nSous-catégorie : {nom_categorie}")

                nom_produit = input(
                    "Nom du produit à rechercher : "
                ).strip()

                if nom_produit:
                    recherches.append(
                        (nom_categorie, nom_produit)
                    )

            if not recherches:
                print("Aucune recherche saisie.")
                continue

        else:
            print("Choix invalide.")
            continue

        nombre_pages = demander_pages()

        confirmation = input(
            "Lancer le scraping ? (o/n) : "
        ).strip().lower()

        if confirmation != "o":
            print("Scraping annulé.")
            continue

        toutes_les_lignes = []

        for categorie, produit in recherches:
            lignes = traiter_recherche(
                categorie,
                produit,
                nombre_pages
            )
            toutes_les_lignes.extend(lignes)

        enregistrer_recap(toutes_les_lignes)

        print("\n========== COLLECTE TERMINÉE ==========")
        print(f"Produits collectés : {len(toutes_les_lignes)}")

        input("\nAppuie sur Entrée pour revenir au menu...")


if __name__ == "__main__":
    afficher_menu()
