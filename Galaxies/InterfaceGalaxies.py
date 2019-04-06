import tkinter as tk
from tkinter import ttk

import baseDonnees
import javaVisualisation
import Main
import webbrowser


class InterfaceGalaxies(tk.Tk):

    def __init__(self):
        """
        Fonction qui va initialiser notre fenetre ainsi que toute nos variables:

        self.:
            - frame_left = La zone gauche de notre affichage
            - frame_right = La zone droite de notre affichage
            - liste_Graphe = La Listebox des graphes contenue dans frame_left
            - graph_selected = La liste des graphes selectionner par l'utilisateur
            - graph_selected_last = Le dernier graphe selectionner par l'utilisateur


        """
        self.main = Main.Main(self)
        super().__init__()
        self.geometry("1200x600")

        self.create_menu() # Creation du menu
        self.grid_propagate(0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.frame_left = tk.Frame(self,height=580,width=550)
        self.frame_left.grid(row=0, column=0,sticky = tk.N+tk.S+tk.W+tk.E)
        self.frame_left.pack_propagate(0)

        self.liste_Graphe = tk.Listbox(self.frame_left,selectmode=tk.MULTIPLE, height = 50,bg="gray88",font=("Helvetica", 12))
        self.liste_Graphe.pack(side=tk.LEFT,fill="both", expand = True)

        scrollbar = tk.Scrollbar(self.frame_left, orient="vertical")
        scrollbar.config(command=self.liste_Graphe.yview)
        scrollbar.pack(side="right", fill= "y")

        self.liste_Graphe.config(yscrollcommand=scrollbar.set)
        self.liste_Graphe.bind('<<ListboxSelect>>', self.select_graph)

        self.frame_right = tk.Frame(self, height=580,width=550)
        self.frame_right.grid(row=0, column=1,sticky=tk.N+tk.S+tk.W+tk.E)
        self.frame_right.pack_propagate(0)

        self.graph_info = tk.Label(self.frame_right, relief=tk.RIDGE)
        self.graph_info.pack(side=tk.TOP,fill="both", expand = True,padx = 2,pady= 2)#grid(row=0, column=0,sticky=tk.N+tk.S+tk.W+tk.E)

        self.frame_right_button = tk.Label(self.frame_right,text = "ok")
        self.frame_right_button.pack(side=tk.BOTTOM,fill="both", expand = False,padx = 2,pady= 2)#grid(row=1, column=0,sticky=tk.N+tk.S+tk.W+tk.E)
        self.create_button_menu()
        # Initialisation des variables
        self.graph_selected = []
        self.graph_selected_last = None

    def create_menu(self):
        menubar = tk.Menu(self)
        menu1 = tk.Menu(menubar,tearoff=0)
        menu1.add_command(label="New project with a text-align file", command=self.main.start_from_existing_file)
        menu1.add_command(label="By Compare 2 corpus", command=self.action2)
        menubar.add_cascade(label="Start", menu=menu1)

        menu2 = tk.Menu(menubar,tearoff=0)
        menu2.add_command(label="Existing project")#, command=self.open_text_align_file)
        menubar.add_cascade(label="Open", menu=menu2)

        menubar.add_command(label = "Quit",command= self.destroy)
        self.config(menu=menubar)

    def create_button_menu(self):
        processing = tk.Frame(self.frame_right_button,height=20,width=20)
        processing.pack(side=tk.TOP,fill="both", expand = True)

        processing.grid_columnconfigure(0, weight=1)
        processing.grid_columnconfigure(2, weight=1)
        processing.grid_rowconfigure(0, weight=1)
        processing.grid_rowconfigure(1, weight=1)
        tk.Label(processing, text="Preprocessing").grid(row=0, column=0,sticky=tk.N+tk.S+tk.W+tk.E)#.pack(side=tk.LEFT,fill="both", expand = True)
        ttk.Separator(processing, orient=tk.VERTICAL).grid(row=0,rowspan = 4, column=1,sticky=tk.N+tk.S)#.pack(side=tk.LEFT, fill="y",padx=3, pady=1)#, expand = True)
        tk.Label(processing, text="Postprocessing").grid(row=0, column=2,sticky=tk.N+tk.S+tk.W+tk.E)#.pack(side=tk.RIGHT,fill="both", expand = True)
        tk.Button(processing, text="Nouvelle Requete",command = self.main.get_requete_preprocessing).grid(row=1,rowspan=3, column=0)
        tk.Button(processing, text="Appliquer un filtre\n sur les noeuds").grid(row=1,rowspan=3, column=2)

        button = tk.Frame(self.frame_right_button)
        button.pack(side=tk.BOTTOM,fill="both", expand = True)
        tk.Button(button, text="Afficher la selection dans un navigateur", command=self.display_graph_webbrowser).pack(pady = 15)#, command=fenetre.quit)

    def open_text_align_file(self):
        return tk.filedialog.askopenfilename(title="Open a file",filetypes=[('tab files','.tab')])

    def action2(self):
        tk.messagebox.showinfo("alerte", "Bravo!")

    def get_requete_from_user(self):

        def recupere():
            if (auteur.get()):
                requete['auteur'] = auteur.get().split()
            if (notauteur.get()):
                requete['-auteur'] = notauteur.get().split()
            if (mcles.get()):
                requete['mots_titre'] = mcles.get().split()
            if (notmcles.get()):
                requete['-mots_titre'] = notmcles.get().split()
            if (date.get()):
                requete['date'] = [int(s) for s in date.get().split() if s.isdigit()]
                if (len(requete['date']) == 0):
                    del requete['date']
                elif (len(requete['date']) == 1):
                    i = 1
                    while (date.get()[i] == ' '):
                        i = i + 1
                    if (date.get()[i] == '-'):
                        requete['date'].insert(0, "-")
                    else:
                        requete['date'].append("-")
                elif (len(requete['date']) == 0):
                    print("Erreur à la déclaration de l'intervalle")
                elif requete['date'][0] > requete['date'][1]:
                    print(
                        "Erreur dans la déclaration de l'intervalle\nDonner en premier argument une date antérieure à la seconde")
            if (empan.get()):
                requete['empan'] = [int(s) for s in empan.get().split() if s.isdigit()].pop()
            if (ltexte_max.get()):
                requete['longueur_texte_maximal'] = [int(s) for s in ltexte_max.get().split() if s.isdigit()].pop(0)
            if (nbnoeuds_min.get()):
                requete['nbre_minimal_noeuds'] = [int(s) for s in nbnoeuds_min.get().split() if s.isdigit()].pop(0)
            fenetre.destroy()

        fenetre = tk.Toplevel()
        fenetre.title("Recherche dans les galaxies")
        fenetre.geometry("800x350")

        instructions = tk.Label(fenetre, text="\nEntrer les critères de recherche\n", font="FreeSerif 14 bold").grid(row=0,column=1)


        lab = tk.Label(fenetre, text="Noms et prénoms d'auteurs présents dans la galaxie :", font="Arial 11").grid(sticky="w", row=1, column=1)
        auteur = tk.Entry(fenetre, width=100)
        auteur.grid(row=1, column=2)

        lab2 = tk.Label(fenetre, text="Noms et prénoms d'auteurs absents de la galaxie :", font="Arial 11").grid(sticky="w", row=2, column=1)
        notauteur = tk.Entry(fenetre, width=100)
        notauteur.grid(row=2, column=2)

        lab3 = tk.Label(fenetre, text="Date de publication :\n(Donner un intervalle)", font="Arial 11").grid(sticky="w",row=3,column=1)
        date = tk.Entry(fenetre, width=80)
        date.insert(0, '[ AAAA - AAAA ]')
        date.grid(sticky="w", row=3, column=2)

        lab4 = tk.Label(fenetre, text="Mots présents dans le titre :", font="Arial 11").grid(sticky="w", row=4, column=1)
        mcles = tk.Entry(fenetre, width=100)
        mcles.grid(row=4, column=2)

        lab5 = tk.Label(fenetre, text="Mots absents des titres :", font="Arial 11").grid(sticky="w", row=5, column=1)
        notmcles = tk.Entry(fenetre, width=100)
        notmcles.grid(row=5, column=2)

        lab6 = tk.Label(fenetre, text="Longueur minimale du texte :", font="Arial 11").grid(sticky="w", row=6, column=1)
        empan = tk.Entry(fenetre, width=30)
        empan.grid(sticky="w", row=6, column=2)

        lab7 = tk.Label(fenetre, text="Longueur minimale du plus long texte de la galaxie :", font="Arial 11").grid(
            sticky="w", row=7, column=1)
        ltexte_max = tk.Entry(fenetre, width=30)
        ltexte_max.grid(sticky="w", row=7, column=2)

        lab8 = tk.Label(fenetre, text="Nombre minimal de noeuds dans la galaxie :", font="Arial 11").grid(sticky="w",row=8, column=1)
        nbnoeuds_min = tk.Entry(fenetre, width=30)
        nbnoeuds_min.grid(sticky="w", row=8, column=2)

        requete = dict()

        space = tk.Label(fenetre, text="\n").grid(row=10)
        bouton = tk.Button(fenetre, text="Valider", command=recupere).grid(row=11, column=2)
        close = tk.Button(fenetre, text="Fermer", command=fenetre.quit).grid(sticky="w", row=11, column=1)
        fenetre.bind("<Return>", lambda e: recupere())
        fenetre.bind("<Escape>", lambda e: fenetre.quit())

        self.wait_window(fenetre)
        return {0:requete}

    def display_graph_list(self):
        """
        Fonction qui affiche dans la partie gauche la liste des graphe
        """
        javaVisualisation.preparationVisualisation()
        listGraph = baseDonnees.getListeGraphe()
        for graph in listGraph:
            self.liste_Graphe.insert(tk.END, graph)

    def display_graph_info(self):
        """
        Fonction qui affiche les information du dernier graphe selectionner
        """
        self.graph_info['text'] = self.graph_selected_last


    def select_graph(self,evt):
        """
        Fonction qui devra afficher les information necessaire dans la box de droite,
        et qui met a jour la liste des graphes selectionner
        """
        w = evt.widget
        index = [graph for graph in w.curselection()]

        self.graph_selected_last = set(self.graph_selected) # On garde la liste de selection precedente
        self.graph_selected = [w.get(ind) for ind in index] # On recuperer la liste de selection courante
        self.graph_selected_last = set(self.graph_selected) - self.graph_selected_last # la difference des deux nous donne le dernier selectionne
        if self.graph_selected_last != set(): # Si on a bien un nouveau graphe selectionne
            self.display_graph_info()         # Alors on l'affiche dans notre fenetre a gauche
        print('last item selected',self.graph_selected_last)


    def display_graph_webbrowser(self):
        if self.graph_selected_last == None: return
        webbrowser.open("/home/marc/Desktop/PLDAC/resultat_Galaxies/index1.html")
        print(self.graph_selected_last)

    def askyesno_txt(self,text,titre = "messagebox"):
        return tk.messagebox.askyesno(titre,text)



if __name__ == '__main__':
    interface = InterfaceGalaxies()
    interface.mainloop()

    #listGraph = baseDonnees.getListeGraphe()
    #listGraph = ["Graphe "+str(i)+" de 4 noeuds" for i in range(100)]
    #interface.display_graph_list()
