from functools import reduce

# ==========================================
# FONCTIONS PURES (Analyse fonctionnelle)
# ==========================================

def filtrer_urgentes(taches):
    """
    Utilise 'filter' pour extraire les taches de priorite 1.
    [cite: 85, 90]
    """
    return list(filter(lambda t: t.priority == 1, taches))

def transformer_titres_majuscules(taches):
    """
    Utilise 'map' pour transformer les titres des taches en majuscules.
    [cite: 88, 90]
    """
    return list(map(lambda t: t.title.upper(), taches))

def calculer_statistiques(taches):
    """
    Utilise 'reduce' pour calculer le nombre de taches terminees.
    [cite: 86, 87, 90]
    """
    if not taches:
        return 0
    
    # On transforme chaque tache en 1 si terminee, 0 sinon, puis on additionne
    return reduce(lambda acc, t: acc + (1 if t.status == "Terminee" else 0), taches, 0)

def calculer_pourcentage_completion(taches):
    """
    Calcule le ratio de completion de maniere fonctionnelle.
    """
    total = len(taches)
    if total == 0:
        return 0
    terminees = calculer_statistiques(taches)
    return (terminees / total) * 100