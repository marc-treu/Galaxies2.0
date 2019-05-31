#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import baseDonnees
import extractionGalaxies
import grapheGalaxies
import visualisationGraphe
import javaVisualisation
import lecture_fic

import time
import os
import webbrowser
import sys


class Galaxie:

    def __init__(self, interface, verbose):
        self.interface = interface
        self.verbose = verbose
        self.project_path = None
        self.query = None  # Query on galaxies (i.e. preprocessing)
        self.filter_ = None  # Query on node (i.e. postprocessing)
        self.max_length_galaxie = 100_000

    def start_from_textalign_file(self):
        """
            Starting a new project with a textAlign file
        """
        self.interface.disabled_window()
        project_directory = '/'.join(os.getcwd().split('/')[:-2])
        file = self.interface.open_text_align_file(project_directory)  # Ask for textAlign file localisation
        if file == () or file == '':
            self.interface.enabled_window()
            return  # if the user cancel

        newdirproject = self.interface.ask_for_project_name()  # Ask for project name
        new_max = self.interface.ask_for_max_length_galaxie(self.max_length_galaxie)
        self.max_length_galaxie = new_max if new_max is not None else self.max_length_galaxie
        if newdirproject == "" or newdirproject is None:
            self.interface.enabled_window()
            return  # if the user cancel or enter a empty word

        self.interface.change_name(newdirproject.split('/')[-1])

        self.project_path = '../projects/' + newdirproject

        self.interface.set_progress_bar_values(5, 100, "creation of project files")
        lecture_fic.init_directory(self.project_path)  # Creation of the project folder
        tt1 = time.clock()
        self.interface.set_progress_bar_values(10, 100, "creation of the Data Base")
        baseDonnees.create_bd(self.project_path)  # Creation of the database
        t1 = time.clock()
        self.interface.set_progress_bar_values(20, 100, "filling the Data Base")
        lecture_fic.lecture(file, self.project_path)  # On remplie notre BD avec notre fichiers .tab
        t2 = time.clock()
        self.print_verbose("Temps de lecture du fichier source: " + format(t2 - t1, 'f') + " sec.")
        self.interface.set_progress_bar_values(50, 100, "creation of the galaxies")
        number_of_node = grapheGalaxies.construction_graphe(self.project_path)
        grapheGalaxies.sauvegarde_graphe(self.project_path)  # Et on le sauvegarde
        self.interface.set_progress_bar_values(70, 100, "saving + split the huge galaxies")
        if number_of_node == 0:
            number_of_node = baseDonnees.maxNoeuds(self.project_path + '/BDs')
        t1 = time.clock()
        extractionGalaxies.extractionComposantesConnexes(number_of_node, self.project_path, self.max_length_galaxie)
        tt2 = time.clock()
        self.print_verbose("Temps total: " + format(tt2 - tt1, 'f') + " sec.")
        t2 = time.clock()
        self.print_verbose("Temps total d'extraction des composantes connexes: " + format(t2 - t1, 'f') + " sec.")
        self.print_verbose("Operation terminée start_from_textAlign_file")
        self._get_all_graph()

    def _get_all_graph(self):
        """
            Function we call when we don't have any current query or filter. It apply a empty Query over the data base
        so we could see the entire Galaxies list.
        """
        extractionGalaxies.galaxies_filter({0: {}}, self.project_path)  # Apply the empty Query
        self.interface.display_graph_list()  # Then Display
        self.interface.enabled_window()  # And finally enable the window

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

    def _execute_query_aux(self, query):
        self.print_verbose("Query executed")
        self.print_verbose("query from user =", query)

        self.interface.set_progress_bar_values(80, 100, "Saving Query")
        lecture_fic.save_query(self.query, self.filter_, self.project_path)

        self.interface.set_progress_bar_values(90, 100, "Display result")
        self.interface.display_graph_list()
        self.print_verbose("Galaxies list display")

        self.interface.enabled_window()

    def _execute_query(self):
        self.interface.set_progress_bar_values(10, 100, "Executing query")
        extractionGalaxies.galaxies_filter(self.query, self.project_path)
        self._execute_query_aux(self.query)

    def _execute_filter(self):
        self.interface.set_progress_bar_values(10, 100, "Executing query")
        if extractionGalaxies.nodes_filter(self.filter_, self.project_path):
            self._execute_query_aux(self.filter_)
        else:
            self.interface.enabled_window()
            self.interface.display_info("Your filter has match 0 node", self.filter_)

    def _disable_window(self):
        """
            Function that disable the window if a project is start. If not it return False

        :return: True if a project is start, False otherwise.
        """

        if self.project_path is None:  # if no project are selected or stared
            self.interface.enabled_window()
            return False

        self.interface.disabled_window()
        return True

    def get_requete_preprocessing(self):
        """
            Function that get the query of the user, execute on the galaxies and then display the result
        """
        if not self._disable_window():  # check if a project is start
            return

        self.print_verbose("start of get_requete_preprocessing")
        self.interface.set_progress_bar_values(5, 100, "Collecting query")
        query = self.interface.get_requete_pre_from_user()

        if query is None:  # if no query were ask on galaxie
            self.interface.enabled_window()
            return

        self._add_query(query)
        if len(self.query) == 0:
            self.interface.enabled_window()
            return
        self._execute_query()

    def get_requete_postprocessing(self):
        """
            Function that get the query of the user, execute on the galaxies and then display the result

        """
        if not self._disable_window():  # check if a project is start
            return

        self.print_verbose("start of get_requete_postprocessing")
        self.interface.set_progress_bar_values(5, 100, "Collecting query")
        filter_ = self.interface.get_requete_post_from_user()
        if filter_ is None:  # if no query were ask on node
            self.interface.enabled_window()
            return

        self._add_filter(filter_)
        if len(self.filter_) == 0:
            self.interface.enabled_window()
            return
        self._execute_filter()

    def new_query(self):
        if self.query is None:
            self.get_requete_preprocessing()
        elif self.interface.ask_for_yes_no_txt("Are you sure you want to erase your Query", "Erase current Query"):
            self.query = None
            baseDonnees.reload_query_table(project_path=self.project_path)
            baseDonnees.reload_filter_table(project_path=self.project_path)
            self.get_requete_preprocessing()

    def undo_query(self):
        if self.query is not None:
            self.interface.disabled_window()
            self.interface.set_progress_bar_values(5, 100, "Suppress last query")
            if len(self.query) == 1:
                self.query = None
                self._get_all_graph()
            else:
                del self.query[len(self.query)-1]
                self._execute_query()

    def _add_query(self, query):
        """
            function that create our query on galaxie, we just add up query enter by the user in a dictionnary,
        where keys are the order of the query were enter, and value a dictionnary which represente the query.
        {0: {'auteur': ['Balzac'], 'mots_titre': ['Goriot']}, ...}

        :param query: The new query the user just enter in
        :type query: A dictionnary which containt a Query, {'auteur': ['Balzac'], 'mots_titre': ['Goriot']}
        """
        if self.query is None:
            self.query = {0: query}
        else:
            self.query[len(self.query)] = query

    def new_filter(self):
        if self.filter_ is None:
            self.get_requete_postprocessing()
        elif self.interface.ask_for_yes_no_txt("Are you sure you want to erase your Filter", "Erase current filter"):
            self.filter_ = None
            baseDonnees.reload_filter_table(project_path=self.project_path)
            self.get_requete_postprocessing()

    def undo_filter(self):
        if self.filter_ is not None:
            self.interface.disabled_window()
            self.interface.set_progress_bar_values(5, 100, "Suppress last query")
            baseDonnees.reload_filter_table(project_path=self.project_path)
            if len(self.filter_) == 1:
                self.filter_ = None
                self._execute_query()
            else:
                del self.filter_[len(self.filter_)-1]
                self._execute_filter()

    def _add_filter(self, filter_):

        if self.filter_ is None:
            self.filter_ = {0: filter_}
        else:
            self.filter_[len(self.filter_)] = filter_

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

        filename = visualisationGraphe.sauveGrapheGalaxie_(id_galaxie, self.project_path)
        javaVisualisation.visualisation(filename, self.project_path)
        javaVisualisation.change_html_graph_display(id_galaxie, self.project_path)

        try:
            if sys.platform == "darwin":
                print('files location =', 'file:///' + self.project_path + '/index.html')
                webbrowser.get('firefox').open('file:///' + self.project_path + '/index.html')
            else:
                webbrowser.get('firefox').open(self.project_path + '/index.html')
            self.print_verbose('file id_galaxie =', id_galaxie, ', open in web browser with firefox')
        except:
            webbrowser.open(self.project_path + '/index.html')

    def display_query(self):
        self.interface.display_info("", self.query)

    def mark_galaxie(self, id_galaxie):
        extractionGalaxies.mark_galaxie_query_table(self.project_path, id_galaxie)

    def get_project_path(self):
        return self.project_path

    def print_verbose(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)
