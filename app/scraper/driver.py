
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def creer_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--lang=fr-FR")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(45)

    driver.get("https://www.amazon.fr/")

    input(
        "\nSi Amazon affiche « Continuer les achats », "
        "clique dessus dans Chrome. "
        "Quand la page Amazon est accessible, "
        "appuie sur Entrée ici pour lancer le scraper..."
    )

    return driver
