import math
import random
import matplotlib.pyplot as plt

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

            ouverture = random.randint(10, 150)
            fermeture = ouverture + random.randint(40, 100)

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
        for ligne in self.matrice_distances :
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

        plt.title("Simulation du Territoire CesiCDP : Fenêtres de Temps & Routes Restreintes", fontsize=14,
                  weight='bold')
        plt.xlabel("Coordonnée X", fontsize=11)
        plt.ylabel("Coordonnée Y", fontsize=11)

        import matplotlib.lines as mlines
        ligne_ok = mlines.Line2D([], [], color='gray', linewidth=1, label='Route Autorisée')
        ligne_ko = mlines.Line2D([], [], color='red', linestyle='--', linewidth=1, label='Route Interdite')
        depot_marker = mlines.Line2D([], [], color='white', markerfacecolor='crimson', marker='s', markersize=10,
                                     label='Dépôt')
        client_marker = mlines.Line2D([], [], color='white', markerfacecolor='dodgerblue', marker='o', markersize=10,
                                      label='Client (Fenêtre)')

        plt.legend(handles=[depot_marker, client_marker, ligne_ok, ligne_ko], loc='upper right')

        plt.grid(True, linestyle=':', alpha=0.6)
        plt.show()

reseau = Reseau(nb_villes=15)
reseau.generer_villes()
reseau.calculer_matrice()

reseau.afficher_matrice()
reseau.afficher_reseau()