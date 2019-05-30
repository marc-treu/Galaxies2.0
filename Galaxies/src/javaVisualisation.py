# -*- coding:utf-8 -*-

import parametres
import webbrowser
import networkx as nx
from networkx.readwrite import json_graph
import json
import visualisationGraphe
import os
import shutil
import re


def preparationVisualisation(project_path):
    if 'jsons' in os.listdir(project_path):
        shutil.rmtree(project_path + "/jsons")
        os.mkdir(project_path + "/jsons")
    count = 0

    galaxies = os.listdir(project_path + "/graphs")
    for i in galaxies:
        visualisation(project_path + "/graphs/" + i, project_path)
        count += 1
    amas = os.listdir(project_path + "/amas")
    for i in amas:
        visualisation(project_path + '/amas/' + i, project_path)
        count += 1


def visualisaton_galaxie(num_galaxie):
    Nom = visualisationGraphe.sauveGrapheGalaxie(num_galaxie)
    visualisation(parametres.DirGraphes + Nom)


def visualisation(fichier, project_path):
    G = nx.read_gexf(fichier)

    data1 = json_graph.node_link_data(G)

    nodes = data1['nodes']
    edges = data1['links']
    for i in edges:
        del i['id']

    nv_nodes = []
    for i in nodes:
        d = dict()
        d["data"] = i
        nv_nodes.append(d)

    nv_edges = []

    for i in edges:
        d = dict()
        d["data"] = i
        nv_edges.append(d)

    del data1["nodes"]
    del data1["links"]

    data1["elements"] = dict()
    data1["elements"]["nodes"] = nv_nodes
    data1["elements"]["edges"] = nv_edges

    tab = [int(s) for s in re.findall(r'\d+', fichier.split("/")[-1])]
    if len(tab) == 1:
        filename = project_path + '/jsons/galaxie_' + str(tab[0]) + '.json'
    elif len(tab) == 2:
        filename = project_path + '/jsons/galaxie_' + str(tab[0]) + '_amas_' + str(tab[1]) + '.json'
    else:
        print(fichier)
        print(tab)

    if filename is not None:
        with open(filename, 'w') as f:
            json.dump(data1, f)


def selectionGrapheAffichage(nomFichier):
    #os.mknod(parametres.DirPgm + 'code2.js')
    #os.mknod(parametres.DirPgm + 'code1.js')
    #print("Appel selection Graphe sur ")
    shutil.copyfile(parametres.DirPgm + 'code1.js', parametres.DirPgm + 'code2.js')
    #print("Copie code1 vers code2")
    destination = open(parametres.DirPgm + 'code1.js', "w")
    source = open(parametres.DirPgm + 'code2.js', "r")
    for line in source:
        # print(line)
        # print(line=="  fetch({mode: 'no-cors'})\n")
        if (line == "fetch()\n"):
            destination.write('fetch(\'' + nomFichier + '\')\n')
        elif (line == "  fetch({mode: 'no-cors'})\n"):
            destination.write('fetch(\'' + nomFichier + '\', {mode :\'no-cors\'})\n')
        else:
            destination.write(line)

    source.close()
    destination.close()
    #print("Fin")


def affichage(nomFichier):
    # print(nomFichier)
    selectionGrapheAffichage(nomFichier)
    webbrowser.open('file:///'+parametres.DirPgm + 'pop-up1.html')
    shutil.copyfile(parametres.DirPgm + 'code2.js', parametres.DirPgm + 'code1.js')
    os.remove(parametres.DirPgm + 'code2.js')


def change_html_graph_display(id_galaxie, project_path):
    """
    Change graph to display on browser, by modify the first line of the javascript
    file.

    filename = the graph file you want to display.
    """
    with open(project_path+'/code.js', 'r') as f:
        lines = f.readlines()   # On lit toute les lignes

    number = [int(s) for s in re.findall(r'\d+', id_galaxie.split("/")[-1])]
    if len(number) == 1:
        filename = 'galaxie_' + str(number[0])
    elif len(number) == 2:
        filename = 'galaxie_' + str(number[0]) + '_amas_' + str(number[1])
    lines[0] = '$.getJSON("jsons/'+filename+'.json", function (data) {\n'
                                # On remplace la premiere
    with open(project_path+'/code.js', 'w') as f:
        f.writelines(lines)     # On re ecrie les lignes dans notre fichier
