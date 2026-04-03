# Choix de l'interface : CLI (Impératif/Objet) ou GUI (Événementiel)
from vues.gui_view import GUIView

if __name__ == "__main__":
    # On lance maintenant la version graphique
    app = GUIView()
    app.lancer()