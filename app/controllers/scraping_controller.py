from app.models.database import Database
from app.scraper.amazon_scraper import AmazonScraper
from app.views.console_view import afficher_produits
from app.views.export_view import exporter_csv


def lancer_scraping():

    print("=" * 50)
    print("          AMAZON SCRAPER")
    print("=" * 50)

    categories = {
        "1": ("Téléphones", "telephones"),
        "2": ("Ordinateurs portables", "ordinateurs-portables"),
        "3": ("Accessoires informatiques", "accessoires-informatiques"),
        "4": ("Livres", "livres"),
        "5": ("Électronique", "electronique"),
        "6": ("Toutes catégories", "")
    }

    print("\nChoisissez une catégorie :")

    for numero, (nom, _) in categories.items():
        print(f"{numero}. {nom}")

    choix = input("\nVotre choix : ").strip()

    if choix not in categories:
        print("Choix invalide.")
        return

    nom_categorie, categorie_url = categories[choix]

    recherche = input(
        "\nEntrez les mots-clés du produit à rechercher : "
    ).strip()

    if not recherche:
        print("Veuillez saisir au moins un mot-clé.")
        return

    scraper = None

    try:

        scraper = AmazonScraper()

        produits = scraper.rechercher(
            recherche=recherche,
            categorie=categorie_url,
            nombre_pages=3
        )

        print("AVANT DATABASE")

        db = Database()

        print("APRES DATABASE")

        for produit in produits:

            db.ajouter_produit(
                produit,
                nom_categorie
            )

        print("PRODUITS ENREGISTRES")

        db.fermer()

        print("DATABASE FERMEE")

        print(
            f"\n{len(produits)} produit(s) trouvé(s)"
        )

        print(
            f"\nCatégorie sélectionnée : {nom_categorie}"
        )

        afficher_produits(
            produits
        )

        if produits:

            choix_export = input(
                "\nVoulez-vous exporter les résultats en CSV ? (o/n) : "
            ).strip().lower()

            if choix_export == "o":

                exporter_csv(
                    produits
                )

                print(
                    "\nExport CSV effectué avec succès."
                )

    except Exception as erreur:

        print(
            f"\nUne erreur est survenue : {erreur}"
        )

    finally:

        if scraper is not None:

            scraper.fermer()