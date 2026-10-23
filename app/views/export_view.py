
import os
import pandas as pd


def exporter_csv(produits):
    dossier = "data"
    os.makedirs(dossier, exist_ok=True)

    chemin = os.path.join(dossier, "data.csv")

    donnees = []

    for produit in produits:
        donnees.append({
            "Nom": produit.nom,
            "Prix": produit.prix,
            "Note": produit.note,
            "Nombre d'avis": produit.nombre_avis,
            "Image": produit.image,
        })

    dataframe = pd.DataFrame(donnees)

    dataframe.to_csv(
        chemin,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nExport CSV réussi : {chemin}")
