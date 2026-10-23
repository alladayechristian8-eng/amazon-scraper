
def nettoyer_texte(texte):
    if not texte:
        return ""

    return " ".join(texte.split())
