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


# import pylab as P

def preparationVisualisation():
    #print("Entré préparation visualisation")
    if 'jsons' in os.listdir(parametres.DirGlobal):
        shutil.rmtree(parametres.DirGlobal + 'jsons')
        #print("Destruction dossier jsons")
        os.mkdir(parametres.DirGlobal + 'jsons')
        #print("Reconstruction dossier jsons")
    count = 0

    galaxies = os.listdir(parametres.DirGraphes)
    for i in galaxies:
        visualisation(parametres.DirGraphes + '/' + i)
        #print("visualisation ",parametres.DirGraphes + '/' + i)
        count += 1
    amas = os.listdir(parametres.DirAmas)
    for i in amas:
        visualisation(parametres.DirAmas + '/' + i)
        #print("visualisation ", parametres.DirGraphes + '/' + i)
        count += 1


def visualisaton_galaxie(num_galaxie):
    Nom = visualisationGraphe.sauveGrapheGalaxie(num_galaxie)
    visualisation(parametres.DirGraphes + Nom)

def visualisation(fichier):
    G = nx.read_gexf(fichier)

    data1 = json_graph.node_link_data(G)

    nodes = data1['nodes']
    edges = data1['links']
    for i in edges:
        del i['id']
    # print(type(nodes))
    # print(len(edges))
    # nv_nodes=dict()

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

    tab = [int(s) for s in re.findall(r'\d+', fichier)]
    if (len(tab) == 1):
        filename = parametres.DirGlobal + 'jsons/galaxie_' + str(tab[0]) + '.json'
    elif (len(tab) == 2):
        filename = parametres.DirGlobal + 'jsons/galaxie_' + str(tab[0]) + '_amas_' + str(tab[1]) + '.json'
    else:
        print(fichier)
        print(tab)

    # print(data1)
    # création d'un fichier json à la répertoire indiquée
    with open(filename, 'w') as f:
        json.dump(data1, f)

# chemin vers le fichier gexf contenant le graphe
# def visualisation(fichier):
#     G = nx.read_gexf(fichier)
#     data1 = json_graph.node_link_data(G)
#
#     nodes = data1['nodes']
#     edges = data1['links']
#     for i in edges:
#         del i['id']
#     # print(type(nodes))
#     # print(len(edges))
#     # nv_nodes=dict()
#
#     nv_nodes = []
#     for i in nodes:
#         d = dict()
#         d["data"] = i
#         nv_nodes.append(d)
#
#     nv_edges = []
#
#     for i in edges:
#         d = dict()
#         d["data"] = i
#         nv_edges.append(d)
#
#     del data1["nodes"]
#     del data1["links"]
#
#     data1["elements"] = dict()
#     data1["elements"]["nodes"] = nv_nodes
#     data1["elements"]["edges"] = nv_edges
#     # print(data1)
#     # création d'un fichier json à la répertoire indiquée
#     with open(parametres.DirAffichage + 'graphe.json', 'w') as f:
#         json.dump(data1, f)
#         # ouvrir le fichier dans le navigateur
#     # b = webbrowser.get(using='firefox')
#     # b.open_new('file://'+ parametres.DirAffichage + 'pop-up1.html')
# #    webbrowser.open_new_tab('file://' + parametres.DirAffichage + 'pop-up1.html')


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
