import random
import networkx as nx #Module axé sur la théorie des graphe
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText #Classe pour la barre de défilement de la table de routage
import matplotlib.pyplot as plt


# Initialisation du graphe au niveau global
graphe = nx.Graph() # On initialise le graphe vide

# Fonction pour construire le graphe
def construire_graphe():
    """ Construire le graphe en respectant la hierarchie des noeuds """
    global graphe  # On fait reference à la variable graphe
    graphe.clear() # On efface le graphe précédent

    # Ajout des nœuds du backbone (Niveau 1)
    noeuds_niveau1 = range(1, 11)
    graphe.add_nodes_from(noeuds_niveau1, niveau=1) # On attribut un attribut niveau aux noeuds

    # Création des arêtes du backbone avec une probabilité de 75%
    for u in noeuds_niveau1:
        for v in noeuds_niveau1:
            if u < v and random.random() < 0.75: 
                poids = random.randint(5, 10) # Poids des arêtes entre les noeuds de niveau 1
                graphe.add_edge(u, v, poids=poids) 

    # Ajout des opérateurs de niveau 2 (Niveau 2)
    noeuds_niveau2 = range(11, 31) # Crée les id des noeuds de niveau 2
    graphe.add_nodes_from(noeuds_niveau2, niveau=2)

    for noeud in noeuds_niveau2:
        voisins_niveau1 = random.sample(noeuds_niveau1, random.randint(1, 2)) 
        # On lie les noeuds de niv2 avec un ou deux noeuds de niveau 1
        for voisin in voisins_niveau1:
            poids = random.randint(10, 20)
            graphe.add_edge(noeud, voisin, poids=poids)


    # Ajout des opérateurs de niveau 3 (Niveau 3)
    noeuds_niveau3 = range(31, 101)
    graphe.add_nodes_from(noeuds_niveau3, niveau=3)

    for noeud in noeuds_niveau3:
        voisins_niveau2 = random.sample(noeuds_niveau2, 2) # On sélctione deux aléatoirement deux noeuds de niv 2 qui seront voisins de chaques noeuds de niv3
        for voisin in voisins_niveau2:
            poids = random.randint(20, 50)
            graphe.add_edge(noeud, voisin, poids=poids)

# Parcours en profondeur pour vérifier la connexité du graphe
def parcours_profondeur(graphe, depart, visite=None):
    """fonction qui fait le parcours en profondeur qui sera utilisé pour verifier la connexité"""
    if visite is None:
        visite = set() # set() pour ne par avoir plusieurs fois les mêmes sommets visités
    visite.add(depart)
    for voisin in graphe[depart]: # Graphe[noeud] -> renvoie les voisins du noeud
        if voisin not in visite:
            parcours_profondeur(graphe, voisin, visite) 
            # Appel récursif de la fonction
    return visite

# Vérification de la connexité
def est_connexe(graphe):
    """ Verifie si le graphe généré par networkx est connexe , si non on regénére un graphe """
    for noeud in graphe.nodes:
        visite = parcours_profondeur(graphe, noeud) # On fait un parcours en profondeur pour chaque noeud
        if len(visite) != len(graphe.nodes): # Compare le nombre de noeuds visités avec le nombres de sommets totaux
            print("Le Graphe n'est pas connexe. Génération d'un nouveau graphe !")
            construire_graphe() # Si le graphe n'est pas connexe on en refait un
            return False
    print("Le Graphe est connexe. Veuillez afficher la table de routage et le Graphe")
    bouton_verif.destroy() # On détruit le bouton de connexité
    # On fait apparaitre les boutons du graphe et de la table de routage
    bouton_graphe = tk.Button(fenetre_principale, text="Afficher Graphe", font=("Arial", 14), command=afficher_graphe)
    bouton_graphe.pack(side=tk.LEFT, padx=20, pady=10)
    bouton_table = tk.Button(fenetre_principale, text="Afficher Tables de Routage", font=("Arial", 14), command=afficher_tables_routage)
    bouton_table.pack(side=tk.RIGHT, padx=20, pady=10)
    return True

# Fonction pour afficher le graphe
def afficher_graphe():
    """ Affichage du graphe """
    global graphe
    fig, ax = plt.subplots(figsize=(12, 8))
    # On crée une figure dans matplotlib. Fig = figure , ax= axe (zone de dessin)
    # figsize=(12, 8) : dimension de la figure 
    
    # Disposition hiérarchique 
    disposition = nx.shell_layout #nx.shell_layout permet de disposer les noeuds en forme de coquille
    niveaux = [[noeud for noeud in graphe if graphe.nodes[noeud]['niveau'] == 1],
               [noeud for noeud in graphe if graphe.nodes[noeud]['niveau'] == 2],
               [noeud for noeud in graphe if graphe.nodes[noeud]['niveau'] == 3]]
    pos = disposition(graphe, nlist=niveaux)  # Ajustez les positions des noeuds selon leurs niveaux 
    # Couleurs par niveau
    carte_couleurs = {1: 'lightblue', 2: 'lightgreen', 3: 'lightcoral'}
    couleurs_noeuds = [carte_couleurs[graphe.nodes[noeud]['niveau']] for noeud in graphe.nodes]
    # On associe la couleur aux noeuds selon leur catégorie

    # Dessiner les composantes du graphe 
    noeuds = nx.draw_networkx_nodes(graphe, pos, node_color=couleurs_noeuds, ax=ax)
    aretes = nx.draw_networkx_edges(graphe, pos, ax=ax)
    etiquettes = nx.draw_networkx_labels(graphe, pos, ax=ax)

    
    def sur_clic(event):
        """ Fonction pour gérer les clics et trouver les chemins """
        ax.clear()  # Effacer les dessins précédents
        noeuds = nx.draw_networkx_nodes(graphe, pos, node_color=couleurs_noeuds, ax=ax)
        aretes = nx.draw_networkx_edges(graphe, pos, ax=ax)
        etiquettes = nx.draw_networkx_labels(graphe, pos, ax=ax)

        # Déterminer le noeud cliqué
        if not hasattr(sur_clic, "premier_noeud"):
            sur_clic.premier_noeud = None

        # Cette partie de la fonction fait en sorte que lorsque l'utilisateur clique à coté d'un noeud
        # Le noeud le plus proche de la zone du clic sera selectionné 
        x, y = event.xdata, event.ydata  # On prend les coordonés du lieu du clic
        distances = {noeud: (x - pos[noeud][0])**2 + (y - pos[noeud][1])**2 for noeud in graphe.nodes} #On calcul la distance entre tous les noeuds et le clic
        noeud_proche = min(distances, key=distances.get)

        if sur_clic.premier_noeud is None:
            sur_clic.premier_noeud = noeud_proche
            nx.draw_networkx_nodes(graphe, pos, nodelist=[noeud_proche], node_color='cyan', ax=ax) # On colore le noeud de départ en rouge
            plt.draw()
        else:
            chemin = nx.dijkstra_path(graphe, source=sur_clic.premier_noeud, target=noeud_proche, weight='poids') # On utilise djikstra pour faire le chemin entre les deux noeuds cliqués en prenant en compte l'attribut "poids" des arêtes
            aretes_chemin = list(zip(chemin[:-1], chemin[1:]))
            nx.draw_networkx_nodes(graphe, pos, nodelist=chemin, node_color='red', ax=ax) # Les noeuds du chemin sont redessinés en rouge
            nx.draw_networkx_edges(graphe, pos, edgelist=aretes_chemin, edge_color='red', width=2, ax=ax)
            plt.draw()
            sur_clic.premier_noeud = None  # Réinitialiser pour la sélection suivante

    fig.canvas.mpl_connect('button_press_event', sur_clic)  # On associe le clic de la souris à la fonction sur_clic()
    plt.show()


def afficher_tables_routage():
    """ Fonction qui permet d'afficher la table de routage """
    fenetre_selection = tk.Toplevel()  # On crée une nouvelle fenêtre par dessus la fenêtre principale
    fenetre_selection.title("Sélectionner un nœud")

    variable_noeud = tk.StringVar()
    etiquette_noeud = ttk.Label(fenetre_selection, text="Sélectionner un nœud de départ :")
    etiquette_noeud.pack(pady=(10, 5))
    combobox_noeud = ttk.Combobox(fenetre_selection, textvariable=variable_noeud, state="readonly") # Création de la combobox qui permet à l'utilisateur de selectionner un noeud de départ
    combobox_noeud['values'] = list(graphe.nodes) # Les valeur à séléctionner représentent tous les noeuds
    combobox_noeud.pack(pady=(0, 10))

    texte_table_routage = ScrolledText(fenetre_selection, width=80, height=30)
    texte_table_routage.pack()

    bouton_afficher = ttk.Button(fenetre_selection, text="Afficher la table de routage", command=lambda: afficher_table_routage_principal(int(variable_noeud.get()), texte_table_routage))
    # Création bouton "afficher table de routage" dans la fenêtre principale
    bouton_afficher.pack(pady=(0, 10))

    def afficher_table_routage_principal(noeud_selectionne, texte):
        distances, chemins = dijkstra(noeud_selectionne) # On utilise Djikstra pour générer les chemins depuis le noeud de départ
        texte.delete('1.0', tk.END) 
        texte.insert(tk.END, f"Table de routage pour le nœud {noeud_selectionne}:\n\n")
        texte.insert(tk.END, f"{'Arrivé':<17} {'Distance':<15} {'Chemin':<40}\n")
        # Placement des colonnes de la table de routage
        for noeud, distance in distances.items():
            chemin = ' -> '.join(map(str, chemins[noeud][::-1] + [noeud])) # On affiche le noeud de départ et son chemin vers le noeud de départ
            texte.insert(tk.END, f"{noeud:<17} {distance:<15} {chemin:<40}\n")


def dijkstra(depart):
    """ Algorithme de Dijkstra pour trouver le chemin le plus court entre deux nœuds """
    global graphe
    distances = {noeud: float('inf') for noeud in graphe} 
    distances[depart] = 0 # Noeud de départ
    chemins = {noeud: [] for noeud in graphe} # Initialise un dictionnaire chemins qui stockera les chemins les plus courts pour chaque nœud.
    visites = set()
    while visites != set(graphe): # Boucle tant que tous les noeuds n'ont pas été visités
        noeud_actuel = min((noeud for noeud in graphe if noeud not in visites), key=lambda n: distances[n])
        # Sélectionne le nœud non visité ayant la plus petite distance parmi ceux accessibles
        visites.add(noeud_actuel)
        for voisin, info_arete in graphe[noeud_actuel].items(): 
            poids = info_arete['poids']
            distance = distances[noeud_actuel] + poids 
            if distance < distances[voisin]: # Si la condition est vérifié : un plus court chemin est trouvé
                distances[voisin] = distance
                chemins[voisin] = [noeud_actuel] + chemins[noeud_actuel]
    return distances, chemins

# Création de l'interface graphique principale
fenetre_principale = tk.Tk()
fenetre_principale.title("Algorithmique de Graphes Projet")
fenetre_principale.geometry("1250x700")
fenetre_principale.resizable(height=False, width=False)

titre_projet = tk.Label(fenetre_principale, text='✨  “Algorithmique de Graphes” Projet : Tables de routage  ✨', font=("Calibri", 20), fg='red', pady=50)
titre_projet.pack()

# Texte explicatif humouristique
texte_humoristique = """
Ah, la création aléatoire d'un réseau réaliste, c'est un peu comme tenter de construire une maison en cartes à jouer pendant un tremblement de terre !\n Mais n'ayez crainte, je suis ici pour transformer ce défi en une comédie pleine de rebondissements et de surprises. \n\nImaginez-vous dans le monde des opérateurs de niveau 1, ces maîtres du réseau, les gardiens du backbone.\n Avec leurs 10 nœuds interconnectés, c'est comme une réunion de famille animée où les données échangent des potins à la vitesse de la lumière.\n Et devinez quoi ? Il y a 75% de chance qu'un lien existe entre ces piliers du réseau.\n Et si ce lien existe, vous pouvez être sûr qu'il est valorisé par un petit numéro de cirque, entre 5 et 10 unités de temps, juste assez pour faire une blague à un routeur ou deux. \n\nMaintenant, plongeons dans le monde des opérateurs de niveau 2, ces intermédiaires de la connexion, jonglant avec les paquets de données comme des acrobates dans un cirque numérique.\n Avec leurs 20 nœuds, ils sont là pour rendre le réseau aussi vivant que possible. \n Et leurs liens ? Entre 10 et 20 unités de temps, juste assez pour une pause café et un petit numéro de jonglage avec les données.\n\nMais n'oublions pas les opérateurs de niveau 3, ces travailleurs acharnés de l'infrastructure, tissant des toiles de connexion avec des fils de cuivre et des fibres optiques.\n Avec leurs 70 nœuds, ils sont les héros discrets du réseau, gardant le monde connecté même dans les moments les plus tumultueux. \n Leurs liens ? Entre 20 et 50 unités de temps, un peu plus de patience est nécessaire, mais après tout, la patience est une vertu numérique. \n\nEt maintenant, pour mémoriser ce joyeux désordre, quelle structure de données choisir ? Un graphe, bien sûr !\n Comme une carte au trésor pour naviguer dans ce monde de fous, nous pourrons trouver notre chemin à travers ce dédale de connexions avec grâce et facilité.\n Alors, prêts à plonger dans cette aventure numérique pleine de rires et de défis ? \n Accrochez-vous bien, car ça va secouer !
"""

# Cadre pour le texte explicatif
cadre1 = tk.Frame(fenetre_principale, bg='black', bd=3, relief="sunken", width= 500, height =300)
text_subtitle1 = tk.Label(cadre1, font=("Arial", 11), fg='black', bg='white', justify="center", text= texte_humoristique)                                                              
text_subtitle1.pack()
cadre1.pack()

# Bouton de la connexité
bouton_verif = tk.Button(fenetre_principale, text="Vérification Connexité", font=("Arial", 14), bg="green", command=lambda: est_connexe(graphe))
bouton_verif.pack(side=tk.TOP, padx=20, pady=10)

# Construire le graphe au démarrage
construire_graphe()

fenetre_principale.mainloop()
