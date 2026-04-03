import json
import os

# Fichier de stockage des données
FICHIER_TACHES = "taches.json"

# ==========================================
# GESTION DU STOCKAGE (Données - Rôle de Victor)
# ==========================================

def charger_taches():
    """Charge les tâches depuis le fichier JSON dans un tableau (liste)."""
    if not os.path.exists(FICHIER_TACHES):
        return [] # Retourne un tableau vide si le fichier n'existe pas
    
    with open(FICHIER_TACHES, 'r', encoding='utf-8') as fichier:
        return json.load(fichier)

def sauvegarder_taches(taches):
    """Sauvegarde le tableau de tâches dans le fichier JSON."""
    with open(FICHIER_TACHES, 'w', encoding='utf-8') as fichier:
        json.dump(taches, fichier, indent=4, ensure_ascii=False)

# ==========================================
# GESTION DES TÂCHES CRUD (Logique - Rôle de Sofian)
# ==========================================

def creer_tache(titre, priorite, date_echeance):
    """(Create) Ajoute une nouvelle tâche."""
    taches = charger_taches()
    
    # Génération d'un ID basique
    nouvel_id = 1
    if len(taches) > 0:
        nouvel_id = taches[-1]["id"] + 1
        
    nouvelle_tache = {
        "id": nouvel_id,
        "titre": titre,
        "statut": "A faire",
        "priorite": priorite, # Ex: 1 (Haute), 2 (Moyenne), 3 (Basse)
        "date_echeance": date_echeance # Format YYYY-MM-DD
    }
    
    taches.append(nouvelle_tache)
    sauvegarder_taches(taches)
    print(f"Tâche créée avec succès : '{titre}'")

def lire_taches():
    """(Read) Affiche toutes les tâches."""
    taches = charger_taches()
    print("\n--- Liste des Tâches ---")
    if not taches:
        print("Aucune tâche trouvée.")
    else:
        for t in taches:
            print(f"[{t['id']}] {t['titre']} | Priorité: {t['priorite']} | Échéance: {t['date_echeance']} | Statut: {t['statut']}")
    print("------------------------\n")

def supprimer_tache(id_tache):
    """(Delete) Supprime une tâche selon son ID."""
    taches = charger_taches()
    # Utilisation d'une boucle classique pour trouver et supprimer (approche impérative)
    index_a_supprimer = -1
    for i in range(len(taches)):
        if taches[i]["id"] == id_tache:
            index_a_supprimer = i
            break
            
    if index_a_supprimer != -1:
        taches.pop(index_a_supprimer)
        sauvegarder_taches(taches)
        print(f"Tâche ID {id_tache} supprimée.")
    else:
        print(f"Tâche ID {id_tache} introuvable.")

def trier_taches_par_priorite():
    """Trie les tâches par priorité (1 étant la plus haute)."""
    taches = charger_taches()
    # Tri utilisant une fonction standard procédurale
    taches_triees = sorted(taches, key=lambda x: x["priorite"])
    return taches_triees

# ==========================================
# ZONE DE TESTS (Vérification du fonctionnement)
# ==========================================

if __name__ == "__main__":
    print("Démarrage des tests du module Impératif...\n")
    
    # 1. Création de quelques tâches de test
    creer_tache("Planifier la campagne marketing", 2, "2023-09-20")
    creer_tache("Approuver l'accord légal", 1, "2023-08-15")
    creer_tache("Mettre à jour la boutique en ligne", 3, "2023-09-15")
    
    # 2. Lecture des tâches
    lire_taches()
    
    # 3. Test du tri par priorité [cite: 68]
    print("--- Test du tri par priorité ---")
    taches_triees = trier_taches_par_priorite()
    for t in taches_triees:
        print(f"Priorité {t['priorite']} : {t['titre']}")
    print("--------------------------------\n")
    
    # 4. Test de suppression
    supprimer_tache(1)
    lire_taches()