import math
import random
import matplotlib.pyplot as plt
import time

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
    def __init__(self, nb_villes=6, largeur=500, hauteur=500, proba_route_barree=0.02):
        self.nb_villes = nb_villes
        self.largeur = largeur
        self.hauteur = hauteur
        self.proba_route_barree = proba_route_barree

        self.villes = []
        self.matrice_distances = []

    def generer_villes(self):
        depot = Ville(0, self.largeur // 2, self.hauteur // 2, 0, 99999)
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


def evaluer_tournee(tournee, reseau):
    """
    Évalue une tournée (liste d'index de villes, ex: [1, 3, 4, 2]).
    Retourne le coût total (distance + pénalités).
    """
    temps_actuel = 0
    distance_totale = 0
    penalites = 0

    trajet_complet = tournee + [0]

    ville_actuelle = 0

    for prochaine_ville in trajet_complet:
        dist = reseau.matrice_distances[ville_actuelle][prochaine_ville]
        if dist == float('inf'):
            penalites += 100000
            dist = 0

        distance_totale += dist
        temps_actuel += dist
        if prochaine_ville != 0:
            client = reseau.villes[prochaine_ville]
            if temps_actuel < client.heure_ouverture:
                temps_actuel = client.heure_ouverture
            elif temps_actuel > client.heure_fermeture:
                retard = temps_actuel - client.heure_fermeture
                penalites += retard * 100
        ville_actuelle = prochaine_ville

    cout_final = distance_totale + penalites

    return cout_final, distance_totale, penalites


def generer_voisin(tournee_actuelle):
    """
    Crée une nouvelle solution en échangeant la position de deux clients au hasard.
    """
    voisin = tournee_actuelle.copy()

    index1 = random.randint(0, len(voisin) - 1)
    index2 = random.randint(0, len(voisin) - 1)

    while index1 == index2:
        index2 = random.randint(0, len(voisin) - 1)

    voisin[index1], voisin[index2] = voisin[index2], voisin[index1]

    return voisin


def recuit_simule(reseau, temp_initiale=200.0, taux_refroidissement=0.99, temp_finale=0.1):
    """
    Exécute l'algorithme du Recuit Simulé pour trouver la meilleure tournée.
    """
    # On crée une liste des clients (de 1 à nb_villes - 1). On exclut le dépôt (0).
    tournee_actuelle = list(range(1, reseau.nb_villes))
    random.shuffle(tournee_actuelle)

    # On évalue cette solution de départ
    cout_actuel, _, _ = evaluer_tournee(tournee_actuelle, reseau)

    meilleure_tournee = tournee_actuelle.copy()
    meilleur_cout = cout_actuel

    temperature = temp_initiale
    historique_couts = []

    while temperature > temp_finale:

        # On génère un voisin (une petite modification)
        voisin = generer_voisin(tournee_actuelle)

        # On évalue ce voisin
        cout_voisin, _, _ = evaluer_tournee(voisin, reseau)

        # Calcul de la différence d'énergie (de coût)
        delta = cout_voisin - cout_actuel

        # - Si delta < 0 : Le voisin est MEILLEUR, on l'accepte
        # - Si delta >= 0 : Le voisin est PIRE. On l'accepte avec une probabilité
        #   qui dépend de la température (plus il fait chaud, plus on accepte l'erreur).
        if delta < 0 or random.random() < math.exp(-delta / temperature):
            # Le mouvement est accepté, on se déplace sur cette nouvelle solution
            tournee_actuelle = voisin
            cout_actuel = cout_voisin

            # Si cette solution est la meilleure jamais vue, on bat le record actuel
            if cout_actuel < meilleur_cout:
                meilleur_cout = cout_actuel
                meilleure_tournee = tournee_actuelle.copy()

        # On sauvegarde le record actuel pour le graphique
        historique_couts.append(meilleur_cout)

        temperature *= taux_refroidissement
    return meilleure_tournee, meilleur_cout, historique_couts


def recuit_simule_multistart(reseau, temp_init, taux_refroid, nb_lancements=5):
    """
    Lance le Recuit Simulé plusieurs fois et ne garde que le record absolu.
    """
    meilleur_cout_global = float('inf')
    meilleure_tournee_globale = None

    for lancement in range(nb_lancements):
        tournee, cout, _ = recuit_simule(reseau, temp_initiale=temp_init, taux_refroidissement=taux_refroid)
        if cout < meilleur_cout_global:
            meilleur_cout_global = cout
            meilleure_tournee_globale = tournee.copy()

    return meilleure_tournee_globale, meilleur_cout_global


def lancer_test_recuit(reseau):
    """
    Teste différentes configurations de paramètres et chronomètre les résultats.
    """
    temperatures_a_tester = [50.0, 200.0, 500.0]
    taux_a_tester = [0.9, 0.95, 0.99]
    nb_multistart = 10

    print(f"Réseau : {reseau.nb_villes - 1} clients | Multi-start : {nb_multistart} lancements par test\n")
    print(f"{'Temp.':<8} | {'Refroid.':<10} | {'Meilleur Coût':<15} | {'Temps de calcul (s)':<18}")
    print("-" * 60)

    resultats_extraits = []

    for t in temperatures_a_tester:
        for taux in taux_a_tester:
            debut_chrono = time.time()

            _, meilleur_cout = recuit_simule_multistart(reseau, t, taux, nb_lancements=nb_multistart)

            fin_chrono = time.time()
            duree = round(fin_chrono - debut_chrono, 3)

            if meilleur_cout > 10000:
                affichage_cout = f"{meilleur_cout} (ÉCHEC)"
            else:
                affichage_cout = f"{round(meilleur_cout, 1)} (SUCCÈS)"

            print(f"{t:<8} | {taux:<10} | {affichage_cout:<15} | {duree:<18}")

            # Sauvegarde des données en mémoire
            resultats_extraits.append({
                'temperature': t,
                'taux': taux,
                'cout': meilleur_cout,
                'temps': duree
            })

    print("-" * 60)
    return resultats_extraits


reseau = Reseau(nb_villes=25)
reseau.generer_villes()
reseau.calculer_matrice()

reseau.afficher_matrice()
reseau.afficher_reseau()

donnees_finales = lancer_test_recuit(reseau)