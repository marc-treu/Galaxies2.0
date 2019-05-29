#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import shelve
import time
import os
import shutil
import sqlite3
import community as louvain
import networkx as nx

import visualisationGraphe
import baseDonnees
import extractionGalaxies


def listeAmas(numGalaxie, project_path):
    listeAmas = shelve.open(project_path + '/BDs/listeAmasGalaxie' + str(numGalaxie))

    print('Récupération de la galaxie ' + str(numGalaxie))
    td = time.clock()
    fichierGrapheGalaxie = visualisationGraphe.sauveGrapheGalaxie(numGalaxie, project_path)
    tf = time.clock()
    print('Galaxie récupérée en ' + format(tf - td, 'f') + 's' + "- sauvegardée dan " + fichierGrapheGalaxie)

    gr = nx.read_gexf(fichierGrapheGalaxie)
    print('Création de la partition de la galaxie')
    td = time.clock()
    amas = louvain.best_partition(gr)
    tf = time.clock()
    print('Partition de ' + str(len(amas)) + ' nœuds créée en ' + format(tf - td, 'f') + 's')
    liste_Amas = dict()
    for x in amas:
        if amas[x] in liste_Amas.keys():
            liste_Amas[amas[x]].append(x)
        else:
            liste_Amas[amas[x]] = [x]
    for a in liste_Amas:
        listeAmas[str(a)] = liste_Amas[a]

    os.remove(fichierGrapheGalaxie)
    listeAmas.close()


def create_partition(nodes_list, project_path):

    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    graph = extractionGalaxies.get_graph_from_nodes(nodes_list, cursor)
    nx_graph = nx.Graph()
    nx_graph.add_nodes_from(list(graph.keys()))
    for key in graph.keys():
        for value in graph[key]:
            nx_graph.add_edge(key, value)

    amas = louvain.best_partition(nx_graph)

    amas_list = dict()
    for ama in amas:
        if amas[ama] in amas_list.keys():
            amas_list[amas[ama]].append(ama)
        else:
            amas_list[amas[ama]] = [ama]

    return amas_list


def recupererAmas(project_path, tailleMinGrosseGalaxie=300):
    noeudsGalaxies = shelve.open(project_path + '/BDs/listeGalaxies')
    j = 0
    td = time.clock()
    while j < baseDonnees.nombreGalaxies(project_path) - 1:
        if len(noeudsGalaxies[str(j)]) > tailleMinGrosseGalaxie:
            print('Galaxie numéro ' + str(j) + ' de taille ' + str(len(noeudsGalaxies[str(j)])) + '\nAppel de Louvain')
            noeudsGalaxies.close()
            listeAmas(j, project_path)
            noeudsGalaxies = shelve.open(project_path + '/BDs/listeGalaxies')

        j += 1
    tf = time.clock()
    if tf - td < 60:
        print('Amas extraits en ' + format(tf - td, 'f') + 's')
    elif tf - td < 3600:
        print('Amas extraits en ' + format((tf - td) / 60, 'f') + 'mn')
    else:
        print('Amas extraits en ' + format((tf - td) / 3600, 'f') + 'h')
    noeudsGalaxies.close()


def execute_query(query, project_path):

    if len(query) == 0:
        return
    extractionGalaxies.galaxies_filter(query, project_path)


def execute_filter(filter_, project_path):

    if len(filter_) == 0:
        return
    extractionGalaxies.nodes_filter(filter_, project_path)
