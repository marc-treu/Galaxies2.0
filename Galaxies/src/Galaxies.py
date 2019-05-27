#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import amas
import baseDonnees
import extractionGalaxies
import grapheGalaxies
import visualisationGraphe
import javaVisualisation
import lecture_fic  

import time
import os
import webbrowser


class Galaxie:

    def __init__(self, interface, verbose):
        self.interface = interface
        self.verbose = verbose
        self.project_path = None
        self.query = None
        self.query_graphs_structure = None

    def get_project_path(self):
        return self.project_path

    def start_from_textalign_file(self, maxNoeud=0, max_length_galaxie=1000000):
        """
            Starting a new project with a textAlign file

        :param maxNoeud:
        :param max_length_galaxie:
        """
        self.interface.disabled_window()
        project_directory = '/'.join(os.getcwd().split('/')[:-2])
        file = self.interface.open_text_align_file(project_directory)  # Ask for textAlign file localisation
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

        lecture_fic.init_directory(self.project_path)  # Creation of the project folder
        tt1 = time.clock()
        baseDonnees.create_bd(self.project_path)  # Creation of the database
        t1 = time.clock()
        lecture_fic.lecture(file, self.project_path)  # On remplie notre BD avec notre fichiers .tab
        t2 = time.clock()
        self.print_verbose("Temps de lecture du fichier source: " + format(t2 - t1, 'f') + " sec.")
        
        maxNoeud = grapheGalaxies.construction_graphe(self.project_path)
        grapheGalaxies.sauvegarde_graphe_(self.project_path)  # Et on le sauvegarde
        if maxNoeud == 0:
            maxNoeud = baseDonnees.maxNoeuds(self.project_path + '/BDs')
        t1 = time.clock()
        extractionGalaxies.extractionComposantesConnexes_(maxNoeud, self.project_path, max_length_galaxie)

        tt2 = time.clock()
        self.print_verbose("Temps total: " + format(tt2 - tt1, 'f') + " sec.")

        t2 = time.clock()
        self.print_verbose("Temps total d'extraction des composantes connexes: " + format(t2 - t1, 'f') + " sec.")
        self.print_verbose("Operation terminée start_from_textAlign_file")
        self.interface.enabled_window()

    def open_existing_project(self):

        self.interface.disabled_window()
        project_directory = '/'.join(os.getcwd().split('/')[:-1]) + '/projects'
        project_list = os.listdir(project_directory)
        if '.gitkeep' in project_list:  # if .gitkeep still in projects folder
            project_list.remove('.gitkeep')  # we delete it
        if not project_list:  # If there is no project
            self.interface.display_info("There are currently zero projects\n on your computer")
            self.interface.enabled_window()
            return

        directory = self.interface.ask_open_existing_project(project_directory)

        if directory == ():
            self.interface.enabled_window()
            return

        if directory.split('/')[-1] not in project_list:  # if the selected folder is not a Galaxie project
            self.interface.display_info("This is not a Galaxie project folder, please select a valid project")
            self.interface.enabled_window()
            return

        self.project_path = directory
        self.interface.change_name(directory.split('/')[-1])
        self.interface.display_graph_list()
        self.query = lecture_fic.load_query(self.project_path)
        text = "The "+self.project_path.split('/')[-1]+" Project has been loaded successfully"
        self.interface.display_info(text, self.query)
        self.interface.enabled_window()

    def _execute_query(self, query):
        amas.requetesUser(query, self.project_path)
        # javaVisualisation.preparationVisualisation(self.project_path)

    def get_requete_preprocessing(self):
        # todo : tache possiblement longue, necessite la progress bar
        self.interface.disabled_window()
        if self.project_path is None:  # if no project are selected or stared
            self.interface.enabled_window()
            return

        self.print_verbose("debut de fonction get_requete_preprocessing")
        query = self.interface.get_requete_from_user()

        self.query = query
        self.print_verbose("la requete = ", self.query)
        if self.query is None:  # if no query were ask on project
            self.interface.enabled_window()
            return

        self._execute_query(self.query)
        lecture_fic.save_query(self.query, self.project_path)
        self.print_verbose("okay ! requete traiter")
        self.interface.display_graph_list()
        self.print_verbose("okay ! graphes afficher")
        self.interface.enabled_window()

    def get_query_graphs_structure(self):
        self.print_verbose("get_query_graphs_structure")
        self.interface.disabled_window()

        if self.query is None:
            self.interface.enabled_window()
            return  # if no query were ask on project

        if self.query_graphs_structure is not None:
            self.print_verbose("self.query_graphs_structure is not None")
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
        return 'Galaxie selected : {}\n\nNumber of nodes : {}\nTotal lengh of text : {}\nMean of text : {}\nlongest ' \
               'text : {}\n'.format(meta_data[0], meta_data[1], meta_data[2], meta_data[3], meta_data[4])

    def display_webbrowser(self, id_galaxie):
        """
            Function that create the files which contains the galaxie id_galaxie, and then display it on web browser

        :param id_galaxie: The id of the galaxie we want to display
        """

        if self.project_path is None:
            return  # if no project are selected or stared

        filename = visualisationGraphe.sauveGrapheGalaxie(id_galaxie, self.project_path)
        javaVisualisation.visualisation(filename, self.project_path)
        javaVisualisation.change_html_graph_display(id_galaxie, self.project_path)

        try:
            webbrowser.get('firefox').open(self.project_path + '/index.html')
            self.print_verbose('file id_galaxie =', id_galaxie, ', open in web browser with firefox')
        except:
            webbrowser.open(self.project_path + '/index.html')
            self.print_verbose('file id_galaxie =', id_galaxie, ', open in web browser with default')

    def mark_galaxie(self, id_galaxie):
        extractionGalaxies.mark_galaxie_query_table(self.project_path, id_galaxie)

    def print_verbose(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)
