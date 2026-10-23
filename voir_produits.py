import sqlite3

connexion = sqlite3.connect("data/amazon.db")
curseur = connexion.cursor()

curseur.execute("SELECT * FROM produits")
produits = curseur.fetchall()

print(f"Nombre de produits : {len(produits)}")

for produit in produits:
    print("-" * 60)
    print(f"ID       : {produit[0]}")
    print(f"Nom      : {produit[1]}")
    print(f"Prix     : {produit[2]}")
    print(f"Note     : {produit[3]}")
    print(f"Avis     : {produit[4]}")
    print(f"Catégorie: {produit[6]}")
    print(f"Marque   : {produit[8]}")

connexion.close()



