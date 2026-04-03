from controleurs.task_controller import TaskController
from analyses.task_analysis import filtrer_urgentes, calculer_pourcentage_completion
from logique.prolog_bridge import PrologBridge

class CLIView:
    def __init__(self):
        # La Vue instancie le Contrôleur pour pouvoir lui envoyer des ordres
        self.controller = TaskController()

    def afficher_menu(self):
        print("\n--- GESTIONNAIRE DE TACHES (MVC) ---")
        print("1. Afficher les taches")
        print("2. Ajouter une tache simple")
        print("3. Ajouter une tache complexe")
        print("4. Voir les analyses (Fonctionnel)")
        print("5. Moteur de Recommandations (Prolog)")
        print("6. Quitter")
        return input("Votre choix (1-6) : ")

    def lancer(self):
        """Boucle principale de l'interface utilisateur."""
        while True:
            choix = self.afficher_menu()
            
            if choix == '1':
                self.afficher_taches()
            elif choix == '2':
                self.ajouter_tache_simple()
            elif choix == '3':
                self.ajouter_tache_complexe()
            elif choix == '4':
                self.afficher_analyses()
            elif choix == '5':
                self.afficher_recommandations()
            elif choix == '6':
                print("Au revoir!")
                break
            else:
                print("Choix invalide. Veuillez reessayer.")

    def afficher_taches(self):
        print("\n--- Liste des taches ---")
        self.controller.charger_taches() # On s'assure d'avoir les dernieres donnees
        taches = self.controller.taches_objets
        
        if not taches:
            print("Aucune tache enregistree.")
        else:
            for t in taches:
                type_t = getattr(t, 'task_type', 'Simple')
                print(f"[{t.id}] {t.title} ({type_t}) - Priorite: {t.priority}")
        print("------------------------")

    def ajouter_tache_simple(self):
        print("\n-- Nouvelle Tache Simple --")
        titre = input("Titre : ")
        priorite = int(input("Priorite (1=Haute, 3=Basse) : "))
        date_e = input("Date d'echeance (YYYY-MM-DD) : ")
        
        # On passe les donnees au controleur, qui se charge du reste
        self.controller.ajouter_tache(titre, priorite, date_e, type_tache="Simple")
        print("Tache simple ajoutee.")

    def ajouter_tache_complexe(self):
        print("\n-- Nouvelle Tache Complexe --")
        titre = input("Titre : ")
        priorite = int(input("Priorite (1=Haute, 3=Basse) : "))
        date_e = input("Date d'echeance (YYYY-MM-DD) : ")
        deps = input("ID des taches dependantes (separes par des virgules, ex: 1,2) : ")
        
        # Transformation de la chaine "1,2" en liste d'entiers [1, 2]
        dependencies = [int(d.strip()) for d in deps.split(',') if d.strip().isdigit()]
        
        self.controller.ajouter_tache(titre, priorite, date_e, type_tache="Complex", dependencies=dependencies)
        print("Tache complexe ajoutee.")

    def afficher_analyses(self):
        print("\n--- ANALYSE FONCTIONNELLE ---")
        taches = self.controller.taches_objets
        
        # 1. Filtrage des urgentes
        urgentes = filtrer_urgentes(taches)
        print(f"Nombre de taches urgentes (Priorite 1) : {len(urgentes)}")
        for u in urgentes:
            print(f" - {u.title}")
            
        # 2. Statistiques de completion
        pourcentage = calculer_pourcentage_completion(taches)
        print(f"Taux de completion global : {pourcentage}%")
        print("----------------------------")

    def afficher_recommandations(self):
        print("\n--- MOTEUR DE RECOMMANDATIONS (PROLOG) ---")
        self.controller.charger_taches()
        taches = self.controller.taches_objets
        
        try:
            bridge = PrologBridge()
            bridge.preparer_faits(taches)
            
            bloquees = bridge.get_taches_bloquees()
            critiques = bridge.get_taches_critiques()
            
            if bloquees:
                print(f"ATTENTION : Les taches avec les ID {bloquees} sont bloquees par une dependance non terminee.")
            else:
                print("Aucune tache n'est bloquee.")
                
            if critiques:
                print(f"URGENCE : Les taches avec les ID {critiques} ont une deadline inferieure a 3 jours.")
            else:
                print("Aucune tache n'est en urgence temporelle.")
                
        except Exception as e:
            print("Erreur de connexion avec Prolog. Verifiez que SWI-Prolog est bien installe.")
            print(f"Details techniques : {e}")
            
        print("------------------------------------------")