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

import time


class Galaxie:

    def __init__(self, interface):
        self.interface = interface
        self.project_path = None
        self.query = None
        self.query_graphs_structure = None

    def get_project_path(self):
        return self.project_path

    def start_from_textalign_file(self, maxNoeud=0):
        """
        Starting a new project with a textAlign file

        :param maxNoeud:
        """
        self.interface.disabled_window()
        file = self.interface.open_text_align_file()  # Ask for textAlign file localisation
        if file == () or file == '':
            self.interface.enabled_window()
            return  # if the user cancel

        newdirproject = self.interface.ask_for_project_name()  # Ask for project name

        if newdirproject == "" or newdirproject is None:
            # todo : Verifier que l'utilisateur n'a pas entrer un nom de project déjà existant
            self.interface.enabled_window()
            return  # if the user cancel or enter a empty word

        self.interface.change_name(newdirproject.split('/')[-1])

        self.project_path = '../projects/' + newdirproject

        lecture_fic.init_directory(self.project_path)  # Creation of the project
        self.interface.set_progress_bar_values(5, 100)
        t1 = time.clock()
        baseDonnees.creerBD(self.project_path + '/BDs')  # Creation of the database
        self.interface.set_progress_bar_values(10, 100)
        t2 = time.clock()
        print("Temps de construction de la base de données: " + format(t2 - t1, 'f') + " sec.")
        t1 = time.clock()
        lecture_fic.lecture(file, self.project_path + '/BDs')  # On remplie notre BD avec notre fichiers .tab
        self.interface.set_progress_bar_values(50, 100)
        t2 = time.clock()
        print("Temps de lecture du fichier source: " + format(t2 - t1, 'f') + " sec.")
        print("premier line de la BD = ", grapheGalaxies.grapheConstruit(self.project_path + '/BDs'))

        maxNoeud = grapheGalaxies.construction_graphe(self.project_path + '/BDs')
        self.interface.set_progress_bar_values(60, 100)
        grapheGalaxies.sauvegarde_graphe_(self.project_path + '/BDs')  # Et on le sauvegarde
        self.interface.set_progress_bar_values(70, 100)
        if maxNoeud == 0:
            maxNoeud = baseDonnees.maxNoeuds(self.project_path + '/BDs')
        t1 = time.clock()
        extractionGalaxies.extractionComposantesConnexes_(maxNoeud, self.project_path + '/BDs')
        self.interface.set_progress_bar_values(80, 100)
        t2 = time.clock()
        print("Temps total d'extraction des composantes connexes: " + format(t2 - t1, 'f') + " sec.")
        self.interface.set_progress_bar_values(90, 100)
        amas.recupererAmas(self.project_path)
        print("Operation terminée start_from_textAlign_file")
        self.interface.enabled_window()
        self.interface.reset_progress_bar()

    def open_existing_project(self):

        self.interface.disabled_window()
        directory = self.interface.ask_open_existing_project()
        # todo : verifier que directory est bien un projet
        self.interface.change_name(directory.split('/')[-1])
        self.project_path = directory
        self.interface.display_graph_list()
        self.query = lecture_fic.load_query(self.project_path)
        self.interface.display_project_info(self.project_path.split('/')[-1], self.query)
        self.interface.enabled_window()

    def _execute_query(self, query):
        amas.requetesUser(query, self.project_path)
        javaVisualisation.preparationVisualisation(self.project_path)

    def get_requete_preprocessing(self):
        # todo : tache possiblement longue, necessite la progress bar
        self.interface.disabled_window()
        if self.project_path is None:  # if no project are selected or stared
            self.interface.enabled_window()
            return

        print("debut de fonction get_requete_preprocessing")
        query = self.interface.get_requete_from_user()

        self.query = query
        print("la requete = ", self.query)
        if self.query is None:  # if no query were ask on project
            self.interface.enabled_window()
            return

        self._execute_query(self.query)
        lecture_fic.save_query(self.query, self.project_path)
        print("okay ! requete traiter")
        self.interface.display_graph_list()
        print("okay ! graphes afficher")
        self.interface.enabled_window()

    def get_query_graphs_structure(self):
        print("get_query_graphs_structure")
        self.interface.disabled_window()

        if self.query is None:
            self.interface.enabled_window()
            return  # if no query were ask on project

        if self.query_graphs_structure is not None:
            print("self.query_graphs_structure is not None")
            # todo : tache possiblement longue, necessite la progress bar
            self._execute_query(self.query)  # if we have already change the list of graphs answer, we rebuild it

        self.query_graphs_structure = self.interface.get_query_graphs_structure_from_user()
        if self.query_graphs_structure is None:
            self.interface.enabled_window()
            return

        self._execute_query({0: dict(self.query_graphs_structure[0], **self.query[0])})
        self.interface.display_graph_list()
        self.interface.enabled_window()

    def get_meta_data_on_galaxie(self, idGalaxie):
        """
            Function that extract multiple meta information about a specific Galaxie, and return a formatted String that
        will be display in our interface

        :param idGalaxie: The id of the Galaxie we want meta-data
        :return: A well formatted String that have meta information on idGalaxie
        """
        meta_data = extractionGalaxies.get_meta_data_from_idGalaxie(self.project_path, idGalaxie)
        return 'Galaxie selected : {}\nNumber of nodes : {}\nTotal lengh of text : {}\nMean of text : {}\nlongest ' \
               'text : {}\n'.format(meta_data[0], meta_data[1], meta_data[2], meta_data[3], meta_data[4])
