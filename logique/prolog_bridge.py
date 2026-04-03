from pyswip import Prolog
from datetime import datetime

class PrologBridge:
    def __init__(self, fichier_regles="logique/moteur_regles.pl"):
        self.prolog = Prolog()
        # On charge le fichier contenant les règles logiques
        self.prolog.consult(fichier_regles)

    def preparer_faits(self, taches_objets):
        """Nettoie les anciens faits et injecte les nouveaux basés sur les objets Python."""
        # 1. Nettoyage de la base de connaissances Prolog pour éviter les doublons
        list(self.prolog.query("retractall(tache(_, _, _))"))
        list(self.prolog.query("retractall(dependance(_, _))"))

        # 2. Injection des nouveaux faits
        for t in taches_objets:
            # Calcul des jours restants pour la règle de priorité
            try:
                date_fin = datetime.strptime(t.due_date, "%Y-%m-%d")
                jours_restants = (date_fin - datetime.now()).days
            except ValueError:
                jours_restants = 999 # Valeur par défaut si le format de date est incorrect

            # On insère le fait dans Prolog : tache(Id, Statut, JoursRestants)
            self.prolog.assertz(f"tache({t.id}, '{t.status}', {jours_restants})")

            # On insère les dépendances si c'est une tâche complexe
            if getattr(t, "task_type", "Simple") == "Complex" and hasattr(t, "dependencies"):
                for dep_id in t.dependencies:
                    self.prolog.assertz(f"dependance({t.id}, {dep_id})")

    def get_taches_bloquees(self):
        """Interroge Prolog pour trouver les tâches bloquées par une dépendance."""
        resultats = list(self.prolog.query("tache_bloquee(X)"))
        return [res["X"] for res in resultats]

    def get_taches_critiques(self):
        """Interroge Prolog pour trouver les tâches avec une deadline très proche."""
        resultats = list(self.prolog.query("tache_critique(X)"))
        return [res["X"] for res in resultats]