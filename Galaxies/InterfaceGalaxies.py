import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk


import baseDonnees


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
        menu1.add_command(label="With a text-align file", command=self.open_text_align_file)
        menu1.add_command(label="Compare 2 corpus", command=self.action2)
        menu1.add_separator()
        menu1.add_command(label="Quitter", command=self.destroy)
        menubar.add_cascade(label="Start", menu=menu1)
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
        tk.Button(processing, text="Nouvelle Requete").grid(row=1,rowspan=3, column=0)
        tk.Button(processing, text="Appliquer un filtre\n sur les noeuds").grid(row=1,rowspan=3, column=2)

        button = tk.Frame(self.frame_right_button)
        button.pack(side=tk.BOTTOM,fill="both", expand = True)
        tk.Button(button, text="Afficher la selection dans un navigateur").pack(pady = 15)#, command=fenetre.quit)



    def open_text_align_file(self):
        filepath = filedialog.askopenfilename(title="Open a file",filetypes=[('tab files','.tab')])
        #ajout du code qui lance galaxy à partir du fichier .tab

    def action2(self):
        messagebox.showinfo("alerte", "Bravo!")

    def display_graphe_list(self,listGraphe):
        """
        Fonction qui affiche dans la partie gauche la liste des graphe
        """
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






if __name__ == '__main__':
    interface = InterfaceGalaxies()

    #listGraph = baseDonnees.getListeGraphe()
    listGraph = ["Graphe "+str(i)+" de 4 noeuds" for i in range(100)]
    interface.display_graphe_list(listGraph)
    interface.mainloop()
    #interface.destroy()
