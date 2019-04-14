#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import amas
import baseDonnees
import extractionGalaxies
import grapheGalaxies
import javaVisualisation
import lecture_fic

import os
import shutil
import time


class Main:

    def __init__(self, interface):
        self.interface = interface
        self.project_path = None
        # todo : faire en sorte que la requete soit enregistrer pour pouvoir etre exploiter plus tard
        self.query = None
        self.query_graphs_structure = False

    def start_from_textAlign_file(self, maxNoeud=0):
        """
        Starting a new project with a textAlign file

        :param maxNoeud:
        """
        self.interface.disabled_window()
        file = self.interface.open_text_align_file()  # Ask for textAlign file localisation
        if file == ():
            self.interface.enabled_window()
            return  # if the user cancel

        newdirproject = self.interface.ask_for_project_name()  # Ask for project name

        if newdirproject == "" or newdirproject is None:
            # todo : Verifier que l'utilisateur n'a pas entrer un nom de project déjà existant
            self.interface.enabled_window()
            return  # if the user cancel or enter a empty word

        self.interface.change_name(newdirproject.split('/')[-1])

        self.project_path = '../projects/' + newdirproject

        self.init_directory()  # Creation of the project
        t1 = time.clock()
        baseDonnees.creerBD(self.project_path + '/BDs')  # Creation of the database
        t2 = time.clock()
        print("Temps de construction de la base de données: " + format(t2 - t1, 'f') + " sec.")
        t1 = time.clock()
        lecture_fic.lecture(file, self.project_path + '/BDs')  # On remplie notre BD avec notre fichiers .tab
        t2 = time.clock()
        print("Temps de lecture du fichier source: " + format(t2 - t1, 'f') + " sec.")
        print("premier line de la BD = ", grapheGalaxies.grapheConstruit(self.project_path + '/BDs'))

        maxNoeud = grapheGalaxies.construction_graphe(self.project_path + '/BDs')
        grapheGalaxies.sauvegarde_graphe_(self.project_path + '/BDs')  # Et on le sauvegarde

        if maxNoeud == 0:
            maxNoeud = baseDonnees.maxNoeuds(self.project_path + '/BDs')
        t1 = time.clock()
        extractionGalaxies.extractionComposantesConnexes_(maxNoeud, self.project_path + '/BDs')
        t2 = time.clock()
        print("Temps total d'extraction des composantes connexes: " + format(t2 - t1, 'f') + " sec.")
        amas.recupererAmas(self.project_path)
        print("Operation terminée start_from_textAlign_file")
        self.interface.enabled_window()

    def open_existing_project(self):

        self.interface.disabled_window()
        directory = self.interface.ask_open_existing_project()
        # todo : verifier que directory est bien un projet
        self.interface.change_name(directory.split('/')[-1])
        self.project_path = directory
        self.interface.display_graph_list()
        self.interface.enabled_window()

    def init_directory(self):
        """
        initialise la creation des dossiers pour recuperer les informations
        """
        os.mkdir(self.project_path)
        os.mkdir(self.project_path + '/BDs')
        os.mkdir(self.project_path + '/amas')
        os.mkdir(self.project_path + '/graphs')
        os.mkdir(self.project_path + '/jsons')
        shutil.copy('./code.js', self.project_path + '/')
        shutil.copy('./index.html', self.project_path + '/')

    def _ask_for_query(self):
        amas.requetesUser(self.query, self.project_path)
        javaVisualisation.preparationVisualisation(self.project_path)

    def get_requete_preprocessing(self):
        # todo : tache possiblement longue, necessite la progress bar

        if self.project_path is None:
            return  # if no project are selected or stared

        print("debut de fonction get_requete_preprocessing")
        query = self.interface.get_requete_from_user()
        self.query = query
        print("la requete = ", self.query)
        self._ask_for_query()
        print("okay ! requete traiter")
        self.interface.display_graph_list()
        print("okay ! graphes afficher")

    def get_query_graphs_structure(self):

        if self.query is None:
            # todo : enleve le pass et remmetre le return, ici uniquement pour le bien des teste
            pass
            #return  # if no query were ask on project

        if self.query_graphs_structure:
            # todo : tache possiblement longue, necessite la progress bar
            self._ask_for_query()  # if we have already change the list of graphs answer, we rebuild it
        query_graphs_structure = self.interface.get_query_graphs_structure_from_user()

    def get_project_path(self):
        return self.project_path
