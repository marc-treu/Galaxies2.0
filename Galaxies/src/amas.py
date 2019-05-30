#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import sqlite3
import community as louvain
import networkx as nx

import extractionGalaxies


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


def execute_query(query, project_path):

    if len(query) == 0:
        return
    extractionGalaxies.galaxies_filter(query, project_path)


def execute_filter(filter_, project_path):

    if len(filter_) == 0:
        return
    extractionGalaxies.nodes_filter(filter_, project_path)
