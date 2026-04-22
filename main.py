import math
import random
import matplotlib.pyplot as plt
import pulp

class Ville:
    def __init__(self, index, x, y, heure_ouverture=0, heure_fermeture=9999):
        self.index = index
        self.x = x
        self.y = y
        self.heure_ouverture = heure_ouverture
        self.heure_fermeture = heure_fermeture

    def __str__(self):
        if self.index == 0:
            return f"Dépôt (x:{self.x}, y:{self.y})"
        return f"Client {self.index} | Pos:({self.x}, {self.y}) | Fenêtre: [{self.heure_ouverture} - {self.heure_fermeture}]"


class Reseau:
    def __init__(self, nb_villes=6, largeur=500, hauteur=500, proba_route_barree=0.05):
        self.nb_villes = nb_villes
        self.largeur = largeur
        self.hauteur = hauteur
        self.proba_route_barree = proba_route_barree
        self.villes = []
        self.matrice_distances = []

    def generer_villes(self):
        depot = Ville(0, self.largeur // 2, self.hauteur // 2, 0, 9999)
        self.villes.append(depot)
        for i in range(1, self.nb_villes):
            x = random.randint(0, self.largeur)
            y = random.randint(0, self.hauteur)
            dist_depuis_depot = math.sqrt((x - depot.x) ** 2 + (y - depot.y) ** 2)
            ouverture = int(dist_depuis_depot) + random.randint(0, 100)
            largeur_fenetre = random.randint(1500, 4000)
            fermeture = ouverture + largeur_fenetre
            client = Ville(i, x, y, ouverture, fermeture)
            self.villes.append(client)

    def calculer_matrice(self):
        self.matrice_distances = []
        for i in range(self.nb_villes):
            ligne = []
            for j in range(self.nb_villes):
                if i == j:
                    ligne.append(0)
                else:
                    ville1 = self.villes[i]
                    ville2 = self.villes[j]
                    dist = math.sqrt((ville1.x - ville2.x) ** 2 + (ville1.y - ville2.y) ** 2)
                    if i != 0 and j != 0 and random.random() < self.proba_route_barree:
                        ligne.append(float('inf'))
                    else:
                        ligne.append(round(dist, 2))
            self.matrice_distances.append(ligne)

    def afficher_matrice(self):
        for ligne in self.matrice_distances:
            print(ligne)

    def afficher_reseau(self):
        plt.figure(figsize=(12, 8))
        for i in range(self.nb_villes):
            for j in range(self.nb_villes):
                if i != j:
                    ville_depart = self.villes[i]
                    ville_arrivee = self.villes[j]
                    if self.matrice_distances[i][j] == float('inf'):
                        plt.plot([ville_depart.x, ville_arrivee.x],
                                 [ville_depart.y, ville_arrivee.y],
                                 color='red', linestyle='--', linewidth=1, alpha=0.5)
                    else:
                        plt.plot([ville_depart.x, ville_arrivee.x],
                                 [ville_depart.y, ville_arrivee.y],
                                 color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
        depot = self.villes[0]
        clients = self.villes[1:]
        x_clients = [ville.x for ville in clients]
        y_clients = [ville.y for ville in clients]
        plt.scatter(x_clients, y_clients, c='dodgerblue', marker='o', s=100, zorder=5, label='Clients')
        plt.scatter(depot.x, depot.y, c='crimson', marker='s', s=150, zorder=5, label='Dépôt')
        for ville in self.villes:
            if ville.index == 0:
                texte = "Dépôt"
            else:
                texte = f"C{ville.index}\n[{ville.heure_ouverture}-{ville.heure_fermeture}]"
            plt.annotate(texte, (ville.x + 8, ville.y + 8),
                         fontsize=9, color='darkslategray', weight='bold',
                         bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        plt.title("Simulation du Territoire CesiCDP : Fenêtres de Temps & Routes Restreintes", fontsize=14, weight='bold')
        plt.xlabel("Coordonnée X", fontsize=11)
        plt.ylabel("Coordonnée Y", fontsize=11)
        import matplotlib.lines as mlines
        ligne_ok = mlines.Line2D([], [], color='gray', linewidth=1, label='Route Autorisée')
        ligne_ko = mlines.Line2D([], [], color='red', linestyle='--', linewidth=1, label='Route Interdite')
        depot_marker = mlines.Line2D([], [], color='white', markerfacecolor='crimson', marker='s', markersize=10, label='Dépôt')
        client_marker = mlines.Line2D([], [], color='white', markerfacecolor='dodgerblue', marker='o', markersize=10, label='Client (Fenêtre)')
        plt.legend(handles=[depot_marker, client_marker, ligne_ok, ligne_ko], loc='upper right')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.show()


    def vers_solveur(self):
        graph = {}
        routes_interdites = set()
        for i in range(self.nb_villes):
            graph[i] = {}
            for j in range(self.nb_villes):
                if i != j:
                    dist = self.matrice_distances[i][j]
                    if dist == float('inf'):
                        graph[i][j] = 99999
                        routes_interdites.add((i, j))
                    else:
                        graph[i][j] = dist
        fenetres_temps = {
            v.index: (v.heure_ouverture, v.heure_fermeture)
            for v in self.villes
        }
        fenetres_temps[0] = (0, 99999)
        return graph, fenetres_temps, routes_interdites


    def afficher_solution(self, chemin, cout):
        plt.figure(figsize=(12, 8))
        for k in range(len(chemin) - 1):
            a, b = chemin[k], chemin[k + 1]
            va, vb = self.villes[a], self.villes[b]
            plt.annotate("", xy=(vb.x, vb.y), xytext=(va.x, va.y),
                         arrowprops=dict(arrowstyle="->", color="limegreen", lw=2.5))
        depot = self.villes[0]
        clients = self.villes[1:]
        plt.scatter([v.x for v in clients], [v.y for v in clients],
                    c='dodgerblue', s=100, zorder=5, label='Clients')
        plt.scatter(depot.x, depot.y, c='crimson', marker='s', s=150, zorder=5, label='Dépôt')
        for v in self.villes:
            texte = "Dépôt" if v.index == 0 else f"C{v.index}\n[{v.heure_ouverture}-{v.heure_fermeture}]"
            plt.annotate(texte, (v.x + 8, v.y + 8), fontsize=9,
                         bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        plt.title(f"Solution TSP (PuLP) — Coût : {cout:.1f}", fontsize=13, weight='bold')
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.tight_layout()
        plt.show()


def resoudre_heuristique(reseau):
    non_visites = [v for v in reseau.villes if v.index != 0]
    ville_actuelle = reseau.villes[0]
    temps_actuel = 0
    tournee = [ville_actuelle]
    distance_totale = 0

    while non_visites:
        meilleure_ville = None
        meilleur_temps_arrivee = float('inf')
        for ville_candidate in non_visites:
            dist = reseau.matrice_distances[ville_actuelle.index][ville_candidate.index]
            if dist == float('inf'):
                continue
            temps_arrivee_prevu = temps_actuel + dist
            temps_debut_service = max(temps_arrivee_prevu, ville_candidate.heure_ouverture)
            if temps_debut_service <= ville_candidate.heure_fermeture:
                if temps_debut_service < meilleur_temps_arrivee:
                    meilleur_temps_arrivee = temps_debut_service
                    meilleure_ville = ville_candidate
        if meilleure_ville is None:
            print("L'heuristique est bloquée : Impossible de livrer tout le monde dans les temps.")
            return None, float('inf'), float('inf')
        tournee.append(meilleure_ville)
        non_visites.remove(meilleure_ville)
        distance_totale += reseau.matrice_distances[ville_actuelle.index][meilleure_ville.index]
        temps_actuel = meilleur_temps_arrivee
        ville_actuelle = meilleure_ville

    dist_retour = reseau.matrice_distances[ville_actuelle.index][0]
    if dist_retour == float('inf'):
        print("Bloqué à la fin. La route de retour vers le dépôt est barrée.")
        return None, float('inf'), float('inf')
    tournee.append(reseau.villes[0])
    distance_totale += dist_retour
    temps_actuel += dist_retour
    return tournee, distance_totale, temps_actuel



def solve_tsp_pulp(graph, fenetres_temps, routes_interdites, penalites={}, depart=0):
    villes = list(graph.keys())
    n = len(villes)
    modele = pulp.LpProblem("TSP_Contraint", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", (villes, villes), cat="Binary")
    temps = pulp.LpVariable.dicts("temps", villes, lowBound=0)
    modele += pulp.lpSum(
        (graph[i][j] + penalites.get((i, j), 0)) * x[i][j]
        for i in villes for j in villes if i != j
    )
    for i in villes:
        modele += pulp.lpSum(x[i][j] for j in villes if i != j) == 1
        modele += pulp.lpSum(x[j][i] for j in villes if i != j) == 1
    for (i, j) in routes_interdites:
        modele += x[i][j] == 0
    u = pulp.LpVariable.dicts("ordre", villes, lowBound=0, upBound=n)
    for i in villes:
        for j in villes:
            if i != j and i != depart and j != depart:
                modele += u[i] - u[j] + n * x[i][j] <= n - 1
    M = 10000
    for i in villes:
        for j in villes:
            if i != j and j != depart:
                modele += temps[j] >= temps[i] + graph[i][j] - M * (1 - x[i][j])
    for i in villes:
        modele += temps[i] >= fenetres_temps[i][0]
        modele += temps[i] <= fenetres_temps[i][1]
    modele += temps[depart] == 0
    modele.solve(pulp.PULP_CBC_CMD(msg=0))
    print("Statut :", pulp.LpStatus[modele.status])
    chemin = [depart]
    courant = depart
    visite = set([depart])
    while True:
        suivant = None
        for j in villes:
            val = pulp.value(x[courant][j])
            if courant != j and val is not None and val > 0.5:
                suivant = j
                break
        if suivant is None or suivant in visite:
            break
        chemin.append(suivant)
        visite.add(suivant)
        courant = suivant
    chemin.append(depart)
    return chemin, pulp.value(modele.objective)


if __name__ == "__main__":
    # ⚠️ nb_villes <= 10 pour PuLP, au-delà utiliser uniquement l'heuristique
    reseau = Reseau(nb_villes=7, proba_route_barree=0.0)
    reseau.generer_villes()
    reseau.calculer_matrice()
    reseau.afficher_reseau()

    # --- Heuristique ---
    tournee, dist, temps = resoudre_heuristique(reseau)
    if tournee:
        print(f"\n[Heuristique] Distance: {dist:.2f} | Temps: {temps:.2f}")

    # --- PuLP ---
    graph, fenetres_temps, routes_interdites = reseau.vers_solveur()
    chemin, cout = solve_tsp_pulp(graph, fenetres_temps, routes_interdites)
    print(f"[PuLP] Chemin : {chemin} | Coût : {cout:.2f}")
    reseau.afficher_solution(chemin, cout)