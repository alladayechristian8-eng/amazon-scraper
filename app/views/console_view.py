
def afficher_produits(produits):
    print("\n" + "=" * 60)
    print(f"{len(produits)} produit(s) trouvé(s)")
    print("=" * 60)

    if not produits:
        print(
            "Aucun produit ne correspond à votre recherche. "
            "Essayez des mots-clés plus simples."
        )
        return

    for numero, produit in enumerate(produits, start=1):
        print(f"\nProduit {numero}")
        print(f"Nom : {produit.nom}")
        print(f"Prix : {produit.prix or 'Non disponible'}")
        print(f"Note : {produit.note or 'Non disponible'}")
        print(
            f"Nombre d'avis : "
            f"{produit.nombre_avis or 'Non disponible'}"
        )
        print(f"Image : {produit.image or 'Non disponible'}")
        print("-" * 60)
