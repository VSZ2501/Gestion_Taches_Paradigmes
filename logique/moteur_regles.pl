:- dynamic tache/3.
:- dynamic dependance/2.

% ==========================================
% FAITS (Exemples de données pour tester le moteur)
% Format: tache(Id, Statut, JoursRestants)
% ==========================================
tache(1, 'Terminee', -5).
tache(2, 'A faire', 15).
tache(3, 'A faire', 2).
tache(4, 'A faire', 10).
tache(5, 'A faire', 20).

% Format: dependance(Tache, DependDe)
% Ex: La tâche 4 dépend de la tâche 3
dependance(4, 3).
dependance(5, 1).

% ==========================================
% RÈGLES LOGIQUES (Le cœur du paradigme)
% ==========================================

% Règle 1 : Une tâche est bloquée SI elle dépend d'une tâche Y ET que Y est 'A faire'.
tache_bloquee(X) :-
    dependance(X, Y),
    tache(Y, 'A faire', _).

% Règle 2 : Une tâche est critique (priorité haute) SI elle est 'A faire' ET que sa deadline est <= 3 jours.
tache_critique(X) :-
    tache(X, 'A faire', JoursRestants),
    JoursRestants =< 3.

% Règle 3 : Une tâche est executable (ordre optimal) SI elle est 'A faire' ET qu'elle n'est pas bloquée.
tache_executable(X) :-
    tache(X, 'A faire', _),
    \+ tache_bloquee(X). % Le \+ signifie la négation logique (NOT)