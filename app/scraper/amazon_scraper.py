
import time
import re
import unicodedata
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By

from app.scraper.driver import creer_driver
from app.models.produit import Produit


INDEX_CATEGORIES = {
    "Téléphones portables et accessoires": "electronics",
    "Informatique": "computers",
    "Audio et vidéo portable": "electronics",
    "TV, vidéo et home cinéma": "electronics",
    "Photo et caméscopes": "electronics",
    "Tablettes PC et liseuses": "electronics",
    "Réseaux et connectivité": "computers",
    "GPS et accessoires": "electronics",
    "Piles et chargeurs": "electronics",
    "Électronique embarquée": "electronics",
    "Radios et accessoires": "electronics",
    "Univers Hi-Fi": "electronics",
}


def normaliser(texte):
    """Met le texte en minuscules et retire les accents."""
    texte = unicodedata.normalize("NFD", texte.lower())
    texte = "".join(
        caractere
        for caractere in texte
        if unicodedata.category(caractere) != "Mn"
    )
    return texte


def nettoyer_prix(texte):
    """Nettoie le texte du prix."""
    return re.sub(r"\s+", " ", texte).strip()


class AmazonScraper:

    def __init__(self):
        self.driver = creer_driver()

    def rechercher(self, recherche, categorie="", nombre_pages=3):
        produits = []
        noms_deja_trouves = set()

        recherche = recherche.strip()

        if not recherche:
            print("Erreur : le nom du produit est vide.")
            return produits

        index = INDEX_CATEGORIES.get(categorie, "electronics")

        # Recherche du produit uniquement :
        # la catégorie est utilisée comme filtre Amazon,
        # pas ajoutée artificiellement aux mots-clés.
        mot_cle = recherche

        termes = normaliser(recherche).split()

        print("\n" + "=" * 55)
        print(f"Catégorie : {categorie or 'Recherche libre'}")
        print(f"Produit recherché : {recherche}")
        print("=" * 55)

        for page in range(1, nombre_pages + 1):

            url = (
                "https://www.amazon.fr/s?k="
                + quote_plus(mot_cle)
                + "&i="
                + quote_plus(index)
                + "&page="
                + str(page)
            )

            print(f"\nPage : {page}")

            self.driver.get(url)
            time.sleep(3)

            elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[data-component-type="s-search-result"]'
            )

            if not elements:
                elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'div.s-result-item[data-asin]'
                )

            if not elements:
                print(
                    "Aucun résultat détecté. "
                    "Vérifie la page Amazon ouverte dans Chrome."
                )
                continue

            for element in elements:
                try:
                    titres = element.find_elements(
                        By.CSS_SELECTOR, "h2"
                    )

                    if not titres:
                        continue

                    nom = titres[0].text.strip()

                    if not nom:
                        continue

                    nom_normalise = normaliser(nom)
                    nom_cle = nom_normalise

                    # Ignore les doublons entre les pages.
                    if nom_cle in noms_deja_trouves:
                        continue

                    # Filtrage simple : tous les mots recherchés
                    # doivent apparaître dans le titre.
                    # Pour une recherche "iPhone 15", cela écarte
                    # les accessoires dont le titre ne contient pas
                    # ces deux termes.
                    if not all(
                        terme in nom_normalise
                        for terme in termes
                    ):
                        continue

                    prix = ""
                    prix_elements = element.find_elements(
                        By.CSS_SELECTOR,
                        ".a-price .a-offscreen"
                    )

                    if prix_elements:
                        prix = nettoyer_prix(
                            prix_elements[0].get_attribute(
                                "textContent"
                            ) or ""
                        )

                    note = ""
                    notes = element.find_elements(
                        By.CSS_SELECTOR,
                        ".a-icon-alt"
                    )

                    for element_note in notes:
                        texte_note = (
                            element_note.get_attribute("textContent")
                            or ""
                        ).strip()

                        if re.search(r"\d", texte_note):
                            note = texte_note
                            break

                    nombre_avis = ""
                    avis = element.find_elements(
                        By.CSS_SELECTOR,
                        "a[href*='customerReviews']"
                    )

                    if avis:
                        nombre_avis = (
                            avis[0].text.strip()
                        )

                    image = ""
                    images = element.find_elements(
                        By.CSS_SELECTOR,
                        "img.s-image"
                    )

                    if images:
                        image = (
                            images[0].get_attribute("src") or ""
                        )

                    produit = Produit(
                        nom=nom,
                        prix=prix,
                        note=note,
                        nombre_avis=nombre_avis,
                        image=image,
                    )

                    produits.append(produit)
                    noms_deja_trouves.add(nom_cle)

                    print(f"Produit trouvé : {nom}")
                    print(f"  Prix : {prix or 'Non disponible'}")
                    print(f"  Note : {note or 'Non disponible'}")
                    print(
                        f"  Avis : "
                        f"{nombre_avis or 'Non disponible'}"
                    )

                except Exception as erreur:
                    print(f"Produit ignoré : {erreur}")

        print(f"\nNombre de produits pertinents : {len(produits)}")

        return produits

    def fermer(self):
        if self.driver:
            self.driver.quit()
