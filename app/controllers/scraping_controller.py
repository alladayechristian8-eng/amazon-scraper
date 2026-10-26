
from app.models.database import Database
from app.scraper.amazon_scraper import AmazonScraper
from app.views.console_view import afficher_produits
from app.views.export_view import exporter_csv


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


def lancer_scraping():

    print("\n" + "=" * 50)
    print("          AMAZON HIGH-TECH")
    print("=" * 50)

    print("\nChoisissez une sous-catégorie :")

    for numero, nom in enumerate(CATEGORIES, start=1):
        print(f"{numero}. {nom}")

    print("0. Recherche sans catégorie")

    choix = input("\nVotre choix : ").strip()

    if choix == "0":
        nom_categorie = ""
    elif choix.isdigit() and 1 <= int(choix) <= len(CATEGORIES):
        nom_categorie = CATEGORIES[int(choix) - 1]
    else:
        print("Choix invalide.")
        return

    recherche = input(
        "\nEntrez le nom du produit à rechercher : "
    ).strip()

    if not recherche:
        print("Veuillez saisir un nom de produit.")
        return

    while True:
        saisie = input(
            "Nombre de pages à parcourir (défaut : 3) : "
        ).strip()

        if not saisie:
            nombre_pages = 3
            break

        if saisie.isdigit() and int(saisie) > 0:
            nombre_pages = int(saisie)
            break

        print("Saisissez un entier supérieur à zéro.")

    scraper = None
    db = None

    try:
        scraper = AmazonScraper()

        produits = scraper.rechercher(
            recherche=recherche,
            categorie=nom_categorie,
            nombre_pages=nombre_pages
        )

        print(f"\nProduits trouvés : {len(produits)}")

        if not produits:
            print("Aucun produit à enregistrer.")
            return

        db = Database()

        for produit in produits:
            db.ajouter_produit(
                produit,
                nom_categorie,
                recherche
            )

        db.connexion.commit()

        print("Produits enregistrés dans SQLite.")
        print(
            "Nombre total de produits dans la base :",
            db.compter_produits()
        )

        afficher_produits(produits)

        choix_export = input(
            "\nExporter les résultats en CSV ? (o/n) : "
        ).strip().lower()

        if choix_export == "o":
            exporter_csv(produits)
            print("Export CSV terminé.")

    except Exception as erreur:
        print(f"\nUne erreur est survenue : {erreur}")

        if db is not None and db.connexion is not None:
            db.connexion.rollback()

    finally:
        if db is not None:
            db.fermer()

        if scraper is not None:
            scraper.fermer()
