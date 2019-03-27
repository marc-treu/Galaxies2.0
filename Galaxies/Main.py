#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import baseDonnees
import grapheGalaxies
import InterfaceGalaxies
import lecture_fic
import os
import parametres

import amas
import extractionGalaxies
import shelve
import time
import visualisationGraphe

import igraph as ig
import networkx as nx
import community as louvain
import Interface
import javaVisualisation
import shutil
import re


class Main:

    def __init__(self):
        self.interface = InterfaceGalaxies.InterfaceGalaxies(self)
        self.interface.mainloop()
        #listGraph = baseDonnees.getListeGraphe()
        #listGraph = ["Graphe "+str(i)+" de 4 noeuds" for i in range(100)]
        #interface.display_graphe_list(listGraph)

    def start_from_existing_file(self):
        file = self.interface.open_text_align_file()
        if file == (): return # Si l'utilisateur a appuié sur cancel
        self.init_dossiers() # creation des dossiers pour stocker les données
        if not 'galaxie.db' in os.listdir(parametres.DirBD): # Si on a pas de bases de donnée
            t1 = time.clock()
            baseDonnees.creerBD()                            # On creer la Base de donnée
            t2 = time.clock()
            print("Temps de construction de la base de données: "+format(t2 - t1,'f')+" sec.")
            t1 = time.clock()
            lecture_fic.lecture(file)                     # On remplie notre BD avec notre fichiers .tab
            t2 = time.clock()
            print("Temps de lecture du fichier source: " + format(t2 - t1,'f') + " sec.")
        print("premier line de la BD = ",grapheGalaxies.grapheConstruit())
        if grapheGalaxies.grapheConstruit()!= None: # On teste si le graphe est construit
            print("Graphe déjà construit")
        else:                                       # Sinon on le construit
            maxNoeud = grapheGalaxies.construction_graphe()
            grapheGalaxies.sauvegarde_graphe_()     # Et on le sauvegarde
        if extractionGalaxies.composantesExtraites() != None:
            print("Composantes déjà extraites")
        else:
            if maxNoeud == 0:
                maxNoeud= baseDonnees.maxNoeuds()
            t1 = time.clock()
            extractionGalaxies.extractionComposantesConnexes_(maxNoeud)
            t2 = time.clock()
            print("Temps total d'extraction des composantes connexes: " + format(t2 - t1,'f') + " sec.")
        amas.recupererAmas()


    def init_dossiers(self):
        """
        initialise la creation des dossiers pour recuperer les informations
        """
        LS = os.listdir(parametres.DirGlobal)
        if not 'BDs' in LS:
            os.mkdir(parametres.DirBD)
        if not 'graphes' in LS:
            os.mkdir(parametres.DirGraphes)
        if not 'amas' in LS:
            os.mkdir(parametres.DirAmas)
        if not 'jsons' in LS:
            os.mkdir(parametres.DirJson)
        if 'galaxie.db' in os.listdir(parametres.DirBD):
            if self.interface.askyesno_txt("Il y a déjà une base de données. Voulez-vous la reconstruire ?"):
                baseDonnees.detruireBD()

    def get_requete_preprocessing(self):
        print("ok")
        requete = self.interface.get_requete_from_user()
        print("ok")
        amas.myRequetesUser(requete)
        print("okay !")

if __name__ == '__main__':
    Main()
