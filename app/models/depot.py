
class Depot:

    def __init__(self):
        self.produits = []
        self.noms_produits = set()

    def ajouter(self, produit):
        if produit.nom in self.noms_produits:
            return False

        self.produits.append(produit)
        self.noms_produits.add(produit.nom)

        return True
