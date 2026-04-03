import json
import os
# Assure-toi d'avoir renommé ton dossier "Modèles" en "modeles"
from modeles.poo_models import SimpleTask, ComplexTask

class TaskController:
    def __init__(self, fichier_stockage="taches.json"):
        self.fichier = fichier_stockage
        self.taches_objets = [] # Liste qui contiendra nos objets Task
        self.charger_taches()

    def charger_taches(self):
        """Charge le JSON et convertit les données brutes en objets Python."""
        if not os.path.exists(self.fichier):
            self.taches_objets = []
            return

        with open(self.fichier, 'r', encoding='utf-8') as f:
            donnees_brutes = json.load(f)
            
        self.taches_objets = []
        for d in donnees_brutes:
            # Polymorphisme basique : on instancie la bonne classe selon la donnée
            if "dependencies" in d and d["dependencies"]:
                tache = ComplexTask(d['id'], d['titre'], d['statut'], d['date_echeance'], d['priorite'], d['dependencies'])
            else:
                tache = SimpleTask(d['id'], d['titre'], d['statut'], d['date_echeance'], d['priorite'])
            
            self.taches_objets.append(tache)

    def sauvegarder_taches(self):
        """Convertit les objets Python en dictionnaires pour les sauvegarder en JSON."""
        donnees_a_sauvegarder = []
        for tache in self.taches_objets:
            tache_dict = {
                "id": tache.id,
                "titre": tache.title,
                "statut": tache.status,
                "priorite": tache.priority,
                "date_echeance": tache.due_date,
                "type": getattr(tache, "task_type", "Simple")
            }
            # Ajout des dépendances seulement si la tâche est complexe
            if hasattr(tache, "dependencies"):
                tache_dict["dependencies"] = tache.dependencies
                
            donnees_a_sauvegarder.append(tache_dict)

        with open(self.fichier, 'w', encoding='utf-8') as f:
            json.dump(donnees_a_sauvegarder, f, indent=4, ensure_ascii=False)

    def ajouter_tache(self, titre, priorite, date_echeance, type_tache="Simple", dependencies=None):
        """Instancie un nouvel objet tâche et le sauvegarde."""
        nouvel_id = 1 if not self.taches_objets else self.taches_objets[-1].id + 1
        
        if type_tache == "Complex":
            nouvelle_tache = ComplexTask(nouvel_id, titre, "A faire", date_echeance, priorite, dependencies)
        else:
            nouvelle_tache = SimpleTask(nouvel_id, titre, "A faire", date_echeance, priorite)
            
        self.taches_objets.append(nouvelle_tache)
        self.sauvegarder_taches()
        print(f"Objet tâche '{titre}' (Type: {type_tache}) instancié et sauvegardé.")