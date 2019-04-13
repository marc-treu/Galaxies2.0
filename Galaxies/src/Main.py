#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import baseDonnees
import grapheGalaxies
import lecture_fic
import os
import parametres

import amas
import extractionGalaxies
import time


class Main:

    def __init__(self, interface):
        self.interface = interface
        self.DirProject = None

    def start_from_textAlign_file(self, maxNoeud=0):
        """
        Starting a new project with a textAlign file

        :param maxNoeud:
        """

        file = self.interface.open_text_align_file()  # Ask for textAlign file localisation
        if file == ():
            return  # if the user cancel

        newdirproject = self.interface.ask_for_project_name()  # Ask for project name

        if newdirproject == "" or newdirproject is None:
            # todo : Verifier que l'utilisateur n'a pas entrer un nom de project déjà existant
            return  # if the user cancel or enter a empty word

        self.DirProject = '../projects/' + newdirproject

        self.init_directory()                        # Creation of the project
        t1 = time.clock()
        baseDonnees.creerBD(self.DirProject+'/BDs')  # Creation of the database
        t2 = time.clock()
        print("Temps de construction de la base de données: "+format(t2 - t1,'f')+" sec.")
        t1 = time.clock()
        lecture_fic.lecture(file, self.DirProject+'/BDs')  # On remplie notre BD avec notre fichiers .tab
        t2 = time.clock()
        print("Temps de lecture du fichier source: " + format(t2 - t1,'f') + " sec.")
        print("premier line de la BD = ", grapheGalaxies.grapheConstruit(self.DirProject+'/BDs'))

        maxNoeud = grapheGalaxies.construction_graphe(self.DirProject+'/BDs')
        grapheGalaxies.sauvegarde_graphe_(self.DirProject+'/BDs')     # Et on le sauvegarde

        if maxNoeud == 0:
            maxNoeud = baseDonnees.maxNoeuds(self.DirProject+'/BDs')
        t1 = time.clock()
        extractionGalaxies.extractionComposantesConnexes_(maxNoeud, self.DirProject+'/BDs')
        t2 = time.clock()
        print("Temps total d'extraction des composantes connexes: " + format(t2 - t1,'f') + " sec.")
        amas.recupererAmas(self.DirProject)
        print("Operation terminée start_from_textAlign_file")

    def open_existing_project(self):

        directory = self.interface.ask_open_existing_project()
        # todo : verifier que directory est bien un projet
        self.DirProject = directory

    def init_directory(self):
        """
        initialise la creation des dossiers pour recuperer les informations
        """
        os.mkdir(self.DirProject)
        os.mkdir(self.DirProject + '/BDs')
        os.mkdir(self.DirProject + '/amas')
        os.mkdir(self.DirProject + '/graphs')
        os.mkdir(self.DirProject + '/jsons')

    def get_requete_preprocessing(self):
        print("debut de fonction")
        requete = self.interface.get_requete_from_user()
        print("la requete = ", requete)
        amas.requetesUser(requete, self.DirProject)
        print("okay ! requete traiter")
        self.interface.display_graph_list()
        print("okay ! graphes afficher")


if __name__ == '__main__':
    main = Main()
    main.interface.mainloop()
