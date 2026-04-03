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
    
    def supprimer_tache(self, task_id):
        """Supprime une tâche et la retire des dépendances des autres."""
        # 1. Supprimer la tâche ciblée
        self.taches_objets = [t for t in self.taches_objets if t.id != task_id]
        
        # 2. Nettoyer les dépendances des tâches restantes
        nouvelles_taches = []
        for t in self.taches_objets:
            if getattr(t, "task_type", "Simple") == "Complex":
                if task_id in getattr(t, "dependencies", []):
                    t.dependencies.remove(task_id)
                    # Si elle n'a plus de dépendances, elle redevient une SimpleTask
                    if len(t.dependencies) == 0:
                        t = SimpleTask(t.id, t.title, t.status, t.due_date, t.priority)
            nouvelles_taches.append(t)
            
        self.taches_objets = nouvelles_taches
        self.sauvegarder_taches()

    def modifier_tache(self, task_id, titre, priorite, date_echeance, statut, dependencies=None):
        """Modifie une tâche et met à jour son type selon ses dépendances."""
        for i, t in enumerate(self.taches_objets):
            if t.id == task_id:
                # Si le champ des dépendances a été manipulé dans le formulaire
                if dependencies is not None:
                    # Polymorphisme : Remplacement de l'objet pour changer son type
                    if len(dependencies) > 0:
                        from modeles.poo_models import ComplexTask
                        self.taches_objets[i] = ComplexTask(task_id, titre, statut, date_echeance, priorite, dependencies)
                    else:
                        from modeles.poo_models import SimpleTask
                        self.taches_objets[i] = SimpleTask(task_id, titre, statut, date_echeance, priorite)
                else:
                    # Garde son type actuel, met juste à jour les champs classiques
                    t.title = titre
                    t.priority = priorite
                    t.due_date = date_echeance
                    t.status = statut
                break
        self.sauvegarder_taches()