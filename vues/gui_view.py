import tkinter as tk
from tkinter import messagebox, ttk, Toplevel
from tkcalendar import DateEntry
from datetime import date, datetime
from controleurs.task_controller import TaskController
from analyses.task_analysis import filtrer_urgentes, calculer_pourcentage_completion
from logique.prolog_bridge import PrologBridge

class GUIView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Projet Paradigme - Gestionnaire de Tâches")
        self.root.geometry("900x550")
        self.controller = TaskController()
        
        self.label_titre = tk.Label(self.root, text="Plateforme de Gestion Intelligente", font=("Arial", 16, "bold"))
        self.label_titre.pack(pady=10)

        # --- Zone d'actions principales ---
        self.frame_ajout = tk.Frame(self.root)
        self.frame_ajout.pack(pady=5)
        
        tk.Button(self.frame_ajout, text="+ Tâche Simple", command=lambda: self.ouvrir_formulaire_ajout("Simple")).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_ajout, text="+ Tâche Complexe", command=lambda: self.ouvrir_formulaire_ajout("Complex")).grid(row=0, column=1, padx=5)
        
        # Séparateur visuel
        tk.Label(self.frame_ajout, text=" | ").grid(row=0, column=2)
        
        # Boutons de modification et suppression
        tk.Button(self.frame_ajout, text="Modifier Sélection", command=self.modifier_selection).grid(row=0, column=3, padx=5)
        tk.Button(self.frame_ajout, text="Supprimer Sélection", command=self.supprimer_selection, fg="red").grid(row=0, column=4, padx=5)

        # --- Tableau des tâches avec l'Échéance ---
        self.colonnes = ("ID", "Titre", "Type", "Priorité", "Statut", "Échéance")
        self.tree = ttk.Treeview(self.root, columns=self.colonnes, show='headings')
        
        for col in self.colonnes:
            # Association de la fonction de tri au clic sur l'en-tête
            self.tree.heading(col, text=col, command=lambda c=col: self.trier_colonne(c, False))
            self.tree.column(col, width=120 if col != "Titre" else 220)
            
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # --- Zone des boutons d'analyse ---
        self.frame_boutons = tk.Frame(self.root)
        self.frame_boutons.pack(pady=10)

        tk.Button(self.frame_boutons, text="Actualiser", command=self.actualiser_liste).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_boutons, text="Analyses", command=self.afficher_stats, bg="#e1f5fe").grid(row=0, column=1, padx=5)
        tk.Button(self.frame_boutons, text="Recommandations", command=self.afficher_prolog, bg="#f1f8e9").grid(row=0, column=2, padx=5)
        tk.Button(self.frame_boutons, text="Quitter", command=self.root.quit).grid(row=0, column=3, padx=5)

        self.actualiser_liste()

    def actualiser_liste(self):
        for i in self.tree.get_children(): 
            self.tree.delete(i)
        self.controller.charger_taches()
        for t in self.controller.taches_objets:
            type_t = getattr(t, 'task_type', 'Simple')
            # Ajout de t.due_date dans les valeurs insérées
            self.tree.insert("", tk.END, values=(t.id, t.title, type_t, t.priority, t.status, t.due_date))

    def trier_colonne(self, col, reverse):
        """Trie le tableau en fonction de la colonne cliquée."""
        donnees = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        
        # Essayer de trier numériquement si c'est l'ID ou la Priorité
        try:
            donnees.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            # Sinon, tri alphabétique/chronologique standard
            donnees.sort(reverse=reverse)

        # Réorganiser les éléments dans l'interface
        for index, (val, k) in enumerate(donnees):
            self.tree.move(k, '', index)

        # Mettre à jour les en-têtes pour afficher la flèche
        for c in self.colonnes:
            self.tree.heading(c, text=c, command=lambda _c=c: self.trier_colonne(_c, False))
        
        symbole = " ▼" if reverse else " ▲"
        self.tree.heading(col, text=col + symbole, command=lambda: self.trier_colonne(col, not reverse))

    def supprimer_selection(self):
        """Supprime la tâche sélectionnée dans le tableau."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à supprimer.")
            return
            
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette tâche ?"):
            # On récupère l'ID de la tâche sélectionnée (colonne 0)
            valeurs = self.tree.item(selection[0], 'values')
            task_id = int(valeurs[0])
            self.controller.supprimer_tache(task_id)
            self.actualiser_liste()

    def modifier_selection(self):
        """Ouvre un formulaire pré-rempli pour modifier une tâche."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à modifier.")
            return
            
        valeurs = self.tree.item(selection[0], 'values')
        task_id = int(valeurs[0])
        titre_actuel = valeurs[1]
        priorite_actuelle = valeurs[3]
        statut_actuel = valeurs[4]
        date_actuelle = valeurs[5]

        fenetre_mod = Toplevel(self.root)
        fenetre_mod.title(f"Modifier la tâche #{task_id}")
        fenetre_mod.geometry("350x300")

        tk.Label(fenetre_mod, text="Titre :").pack(pady=2)
        entree_titre = tk.Entry(fenetre_mod, width=30)
        entree_titre.insert(0, titre_actuel)
        entree_titre.pack(pady=2)
        
        tk.Label(fenetre_mod, text="Priorité (1=Haute, 3=Basse) :").pack(pady=2)
        entree_priorite = tk.Entry(fenetre_mod, width=10)
        entree_priorite.insert(0, priorite_actuelle)
        entree_priorite.pack(pady=2)

        tk.Label(fenetre_mod, text="Statut :").pack(pady=2)
        entree_statut = ttk.Combobox(fenetre_mod, values=["A faire", "En cours", "Terminee"], state="readonly")
        entree_statut.set(statut_actuel)
        entree_statut.pack(pady=2)
        
        tk.Label(fenetre_mod, text="Date d'échéance :").pack(pady=2)
        entree_date = DateEntry(fenetre_mod, width=12, background='darkblue', 
                                foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        # On définit la date du widget sur la date actuelle de la tâche
        try:
            date_obj = datetime.strptime(date_actuelle, "%Y-%m-%d").date()
            entree_date.set_date(date_obj)
        except ValueError:
            pass
        entree_date.pack(pady=2)

        def sauvegarder_modification():
            nouveau_titre = entree_titre.get()
            nouveau_statut = entree_statut.get()
            nouvelle_date = entree_date.get()
            
            try:
                nouvelle_priorite = int(entree_priorite.get())
            except ValueError:
                messagebox.showerror("Erreur", "La priorité doit être un nombre.", parent=fenetre_mod)
                return

            self.controller.modifier_tache(task_id, nouveau_titre, nouvelle_priorite, nouvelle_date, nouveau_statut)
            fenetre_mod.destroy()
            self.actualiser_liste()

        tk.Button(fenetre_mod, text="Enregistrer les modifications", command=sauvegarder_modification, bg="#fff9c4").pack(pady=15)

    def ouvrir_formulaire_ajout(self, type_tache):
        fenetre_ajout = Toplevel(self.root)
        fenetre_ajout.title(f"Nouvelle Tâche {type_tache}")
        fenetre_ajout.geometry("350x250" if type_tache == "Simple" else "350x300")
        
        tk.Label(fenetre_ajout, text="Titre :").pack(pady=2)
        entree_titre = tk.Entry(fenetre_ajout, width=30)
        entree_titre.pack(pady=2)
        
        tk.Label(fenetre_ajout, text="Priorité (1=Haute, 3=Basse) :").pack(pady=2)
        entree_priorite = tk.Entry(fenetre_ajout, width=10)
        entree_priorite.pack(pady=2)
        
        tk.Label(fenetre_ajout, text="Date d'échéance (YYYY-MM-DD) :").pack(pady=2)
        entree_date = DateEntry(fenetre_ajout, width=12, background='darkblue', 
                                foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        entree_date.pack(pady=2)

        entree_deps = None
        if type_tache == "Complex":
            tk.Label(fenetre_ajout, text="ID Dépendances (ex: 1,2) :").pack(pady=2)
            entree_deps = tk.Entry(fenetre_ajout, width=15)
            entree_deps.pack(pady=2)

        def sauvegarder_nouvelle_tache():
            titre = entree_titre.get()
            if not titre.strip():
                messagebox.showerror("Erreur", "Le titre ne peut pas être vide.", parent=fenetre_ajout)
                return

            try:
                priorite = int(entree_priorite.get())
            except ValueError:
                messagebox.showerror("Erreur", "La priorité doit être un nombre.", parent=fenetre_ajout)
                return
            
            date_selectionnee_obj = entree_date.get_date()
            if date_selectionnee_obj < date.today():
                messagebox.showerror("Erreur", "La date d'échéance ne peut pas être dans le passé.", parent=fenetre_ajout)
                return
            
            date_echeance = entree_date.get()
            dependencies = []
            if type_tache == "Complex" and entree_deps:
                deps_brutes = entree_deps.get()
                dependencies = [int(d.strip()) for d in deps_brutes.split(',') if d.strip().isdigit()]

            self.controller.ajouter_tache(titre, priorite, date_echeance, type_tache, dependencies)
            fenetre_ajout.destroy()
            self.actualiser_liste()

        tk.Button(fenetre_ajout, text="Valider", command=sauvegarder_nouvelle_tache, bg="#dcedc8").pack(pady=15)

    def afficher_stats(self):
        taches = self.controller.taches_objets
        pourcentage = calculer_pourcentage_completion(taches)
        urgentes = len(filtrer_urgentes(taches))
        messagebox.showinfo("Analyses Fonctionnelles", 
                            f"Taux de complétion : {pourcentage:.1f}%\n"
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