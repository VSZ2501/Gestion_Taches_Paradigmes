import tkinter as tk
from tkinter import messagebox, ttk, Toplevel
from controleurs.task_controller import TaskController
from analyses.task_analysis import filtrer_urgentes, calculer_pourcentage_completion
from logique.prolog_bridge import PrologBridge

class GUIView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Projet Paradigme - Gestionnaire de Tâches")
        self.root.geometry("800x500")
        self.controller = TaskController()
        
        # --- Titre ---
        self.label_titre = tk.Label(self.root, text="Plateforme de Gestion Intelligente", font=("Arial", 16, "bold"))
        self.label_titre.pack(pady=10)

        # --- Zone d'actions principales (Ajout) ---
        self.frame_ajout = tk.Frame(self.root)
        self.frame_ajout.pack(pady=5)
        
        tk.Button(self.frame_ajout, text="+ Ajouter Tâche Simple", command=lambda: self.ouvrir_formulaire_ajout("Simple")).grid(row=0, column=0, padx=10)
        tk.Button(self.frame_ajout, text="+ Ajouter Tâche Complexe", command=lambda: self.ouvrir_formulaire_ajout("Complex")).grid(row=0, column=1, padx=10)

        # --- Tableau des tâches ---
        self.tree = ttk.Treeview(self.root, columns=("ID", "Titre", "Type", "Priorité", "Statut"), show='headings')
        for col in ("ID", "Titre", "Type", "Priorité", "Statut"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120 if col != "Titre" else 250)
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # --- Zone des boutons d'analyse (Événementiel) ---
        self.frame_boutons = tk.Frame(self.root)
        self.frame_boutons.pack(pady=10)

        tk.Button(self.frame_boutons, text="Actualiser", command=self.actualiser_liste).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_boutons, text="Analyses (Stats)", command=self.afficher_stats, bg="#e1f5fe").grid(row=0, column=1, padx=5)
        tk.Button(self.frame_boutons, text="Recommandations (AI)", command=self.afficher_prolog, bg="#f1f8e9").grid(row=0, column=2, padx=5)
        tk.Button(self.frame_boutons, text="Quitter", command=self.root.quit).grid(row=0, column=3, padx=5)

        # Premier chargement
        self.actualiser_liste()

    def actualiser_liste(self):
        for i in self.tree.get_children(): 
            self.tree.delete(i)
        self.controller.charger_taches()
        for t in self.controller.taches_objets:
            type_t = getattr(t, 'task_type', 'Simple')
            self.tree.insert("", tk.END, values=(t.id, t.title, type_t, t.priority, t.status))

    def ouvrir_formulaire_ajout(self, type_tache):
        """Ouvre une fenêtre modale pour ajouter une tâche."""
        fenetre_ajout = Toplevel(self.root)
        fenetre_ajout.title(f"Nouvelle Tâche {type_tache}")
        fenetre_ajout.geometry("350x250" if type_tache == "Simple" else "350x300")
        
        # Champs du formulaire
        tk.Label(fenetre_ajout, text="Titre :").pack(pady=2)
        entree_titre = tk.Entry(fenetre_ajout, width=30)
        entree_titre.pack(pady=2)
        
        tk.Label(fenetre_ajout, text="Priorité (1=Haute, 3=Basse) :").pack(pady=2)
        entree_priorite = tk.Entry(fenetre_ajout, width=10)
        entree_priorite.pack(pady=2)
        
        tk.Label(fenetre_ajout, text="Date d'échéance (YYYY-MM-DD) :").pack(pady=2)
        entree_date = tk.Entry(fenetre_ajout, width=15)
        entree_date.pack(pady=2)

        entree_deps = None
        if type_tache == "Complex":
            tk.Label(fenetre_ajout, text="ID Dépendances (ex: 1,2) :").pack(pady=2)
            entree_deps = tk.Entry(fenetre_ajout, width=15)
            entree_deps.pack(pady=2)

        def sauvegarder_nouvelle_tache():
            """Fonction interne déclenchée par le bouton Valider."""
            titre = entree_titre.get()
            try:
                priorite = int(entree_priorite.get())
            except ValueError:
                messagebox.showerror("Erreur", "La priorité doit être un nombre.", parent=fenetre_ajout)
                return
            date_echeance = entree_date.get()
            
            dependencies = []
            if type_tache == "Complex" and entree_deps:
                deps_brutes = entree_deps.get()
                dependencies = [int(d.strip()) for d in deps_brutes.split(',') if d.strip().isdigit()]

            # Appel au contrôleur pour l'ajout
            self.controller.ajouter_tache(titre, priorite, date_echeance, type_tache, dependencies)
            
            # Fermeture de la fenêtre et actualisation
            fenetre_ajout.destroy()
            self.actualiser_liste()

        tk.Button(fenetre_ajout, text="Valider", command=sauvegarder_nouvelle_tache, bg="#dcedc8").pack(pady=15)

    def afficher_stats(self):
        taches = self.controller.taches_objets
        pourcentage = calculer_pourcentage_completion(taches)
        urgentes = len(filtrer_urgentes(taches))
        messagebox.showinfo("Analyses Fonctionnelles", 
                            f"Taux de complétion : {pourcentage}%\n"
                            f"Tâches prioritaires détectées : {urgentes}")

    def afficher_prolog(self):
        try:
            bridge = PrologBridge()
            bridge.preparer_faits(self.controller.taches_objets)
            bloquees = bridge.get_taches_bloquees()
            critiques = bridge.get_taches_critiques()
            
            message = f"Tâches bloquées : {bloquees if bloquees else 'Aucune'}\n"
            message += f"Tâches en urgence absolue : {critiques if critiques else 'Aucune'}"
            messagebox.showinfo("Moteur Logique (Prolog)", message)
        except Exception as e:
            messagebox.showerror("Erreur Prolog", f"Impossible de contacter le moteur logique : {e}")

    def lancer(self):
        self.root.mainloop()