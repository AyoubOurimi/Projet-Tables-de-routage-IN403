import random
import networkx as nx
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

# Création du graphe
graphe = nx.Graph()

# Ajout des nœuds du backbone (Tier 1)
noeuds_backbone = range(1, 11)
graphe.add_nodes_from(noeuds_backbone, niveau=1)

# Création des arêtes du backbone avec une probabilité de 75%
for u in noeuds_backbone:
    for v in noeuds_backbone:
        if u < v and random.random() < 0.75:
            poids = random.randint(5, 10)  # Plage de poids pour le Tier 1
            graphe.add_edge(u, v, poids=poids)

# Ajout des opérateurs de niveau 2 (Tier 2)
noeuds_tier2 = range(11, 31)
graphe.add_nodes_from(noeuds_tier2, niveau=2)

for noeud in noeuds_tier2:
    voisins_backbone = random.sample(noeuds_backbone, random.randint(1, 2))
    for voisin in voisins_backbone:
        poids = random.randint(10, 20)  # Plage de poids pour le Tier 2
        graphe.add_edge(noeud, voisin, poids=poids)


# Ajout des opérateurs de niveau 3 (Tier 3)
noeuds_tier3 = range(31, 101)
graphe.add_nodes_from(noeuds_tier3, niveau=3)

for noeud in noeuds_tier3:
    voisins_tier2 = random.sample(noeuds_tier2, 2)
    
    for voisin in voisins_tier2:
        poids = random.randint(20, 50)  # Plage de poids pour le Tier 3
        graphe.add_edge(noeud, voisin, poids=poids)

# Algorithme de Dijkstra pour trouver le chemin le plus court entre deux nœuds
def dijkstra(graphe, depart):
    # Initialisation des distances avec une valeur infinie pour tous les nœuds
    distances = {noeud: float('inf') for noeud in graphe}
    distances[depart] = 0
    
    # Initialisation des chemins avec une liste vide pour tous les nœuds
    chemins = {noeud: [] for noeud in graphe}
    
    # Liste pour stocker les nœuds visités
    visites = set()
    
    while visites != set(graphe):
        # Trouver le nœud non visité avec la distance minimale
        noeud_actuel = min((noeud for noeud in graphe if noeud not in visites), key=lambda n: distances[n])
        visites.add(noeud_actuel)
        
        # Mettre à jour les distances et les chemins pour les voisins du nœud actuel
        for voisin, data_arete in graphe[noeud_actuel].items():
            poids = data_arete['poids']
            distance = distances[noeud_actuel] + poids
            
            if distance < distances[voisin]:
                distances[voisin] = distance
                chemins[voisin] = chemins[noeud_actuel] + [noeud_actuel]
    
    return distances, chemins
# Algorithme de Dijkstra pour trouver le chemin le plus court entre deux nœuds
def dijkstra(graphe, depart):
    # Initialisation des distances avec une valeur infinie pour tous les nœuds
    distances = {noeud: float('inf') for noeud in graphe}
    distances[depart] = 0
    
    # Initialisation des chemins avec une liste vide pour tous les nœuds
    chemins = {noeud: [] for noeud in graphe}
    
    # Liste pour stocker les nœuds visités
    visites = set()
    
    while visites != set(graphe):
        # Trouver le nœud non visité avec la distance minimale
        noeud_actuel = min((noeud for noeud in graphe if noeud not in visites), key=lambda n: distances[n])
        visites.add(noeud_actuel)
        
        # Mettre à jour les distances et les chemins pour les voisins du nœud actuel
        for voisin, data_arete in graphe[noeud_actuel].items():
            poids = data_arete['poids']
            distance = distances[noeud_actuel] + poids
            
            if distance < distances[voisin]:
                distances[voisin] = distance
                chemins[voisin] = [noeud_actuel] + chemins[noeud_actuel]  # Ajout au début du chemin
    
    return distances, chemins

def afficher_table_routage():
    # creation de la nouvelle fenêtre
    fenetre_selection = tk.Toplevel()
    fenetre_selection.title("Sélectionner un nœud")
    
    # combobox pour sélectionner le nœud
    variable_noeud = tk.StringVar()
    etiquete_noeud = ttk.Label(fenetre_selection, text="Sélectionner un nœud :")
    etiquete_noeud.pack(pady=(10, 5))
    combobox_noeud = ttk.Combobox(fenetre_selection, textvariable=variable_noeud, state="readonly")
    combobox_noeud['values'] = list(graphe.nodes)
    combobox_noeud.pack(pady=(0, 10))
    
    # Texte pour afficher la table de routage
    texte_table_routage = ScrolledText(fenetre_selection, width=80, height=30)  # Augmentation de la taille
    texte_table_routage.pack()  # pack(fill=tk.BOTH, expand=True) pour remplir la fenêtre
    
    # Bouton pour afficher la table de routage
    bouton_afficher = ttk.Button(fenetre_selection, text="Afficher la table de routage", command=lambda: afficher_table_routage_principal(variable_noeud.get(), texte_table_routage))
    bouton_afficher.pack(pady=(0, 10))
    
    # fonction pour afficher la table de routage dans la partie texte
    def afficher_table_routage_principal(noeud_selectionne, texte):
        distances, chemins = dijkstra(graphe, int(noeud_selectionne))
        print(graphe)
        texte.delete('1.0', tk.END)  # effacer le contenu précédent
        texte.insert(tk.END, f"Table de routage pour le nœud {noeud_selectionne}:\n\n")
        texte.insert(tk.END, f"{'Arrivé':<17} {'Distance':<15} {'Chemin':<40}\n")
        for noeud, distance in distances.items():
            chemin = ' <- '.join(map(str, [noeud] + chemins[noeud])) # Inversion du chemin
            texte.insert(tk.END, f"{noeud:<17} {distance:<15} {chemin:<40}\n")

    
    # Redimensionnement de la nouvelle fenêtre
    fenetre_selection.geometry("800x600")  # Ajustement de la taille
    

# Création de la fenêtre principale
fenetre_intro = tk.Tk()
fenetre_intro.title("Algorithmique de Graphes Projet")
fenetre_intro.geometry("1000x550")
fenetre_intro.resizable(height=False, width=False)

# Titre
titre_projet = tk.Label(fenetre_intro, text='✨  “Algorithmique de Graphes” Projet : Tables de routage  ✨', font=("Calibri", 20), fg='black', pady=50)
titre_projet.pack()

# Cadre pour le texte explicatif
cadre1 = tk.Frame(fenetre_intro, bg='black', bd=3, relief="sunken", width= 500, height =300)
text_subtitle1 = tk.Label(cadre1, font=("Arial", 13), fg='black', bg='white', justify="left", text="                                                        Mécanisme du Projet + Explication 2.1                                                                 \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
text_subtitle1.pack()
cadre1.pack()

# Bouton pour afficher le graphe (à implémenter)
bouton1 = tk.Button(fenetre_intro, text="Afficher Graphe", font=("Arial", 14))
bouton1.pack(side=tk.LEFT, padx=20, pady=10)

bouton2 = tk.Button(fenetre_intro, text="Afficher Tables de Routage", font=("Arial", 14), command=afficher_table_routage)
bouton2.pack(side=tk.RIGHT, padx=20, pady=10)

fenetre_intro.mainloop()
