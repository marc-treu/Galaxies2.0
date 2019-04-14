#!/bin/env python
# -*- coding: utf-8 -*-
#

import re
import baseDonnees


def handle_query_graph_struture(query, project_path):
    """

    :param query: a dict with specific information about graph query:
                    - minimal_node_number   # minimal number of node for a graph
                    - maximal_node_number   # maximal number of node for a graph
    :param project_path: the path of the current project
    :return:
    """

    list_graph = baseDonnees.get_list_graph(project_path)
    #list_graph = sorted(list_graph, key=lambda x: int(re.findall(r'\d+', str(x))[-1]))[::-1]

    if query['minimal_node_number']:
        list_graph = [graph for graph in list_graph if int(re.findall(r'\d+', str(graph))[-1]) > query['minimal_node_number']]
    if query['maximal_node_number']:
        list_graph = [graph for graph in list_graph if int(re.findall(r'\d+', str(graph))[-1]) > query['maximal_node_number']]

    return list_graph

