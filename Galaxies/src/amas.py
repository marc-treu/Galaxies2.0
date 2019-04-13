#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import shelve
import time
import community as louvain
import os
import shutil
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


def requetesUser(requetes, project_path):
    l = len(requetes)
    if l == 0:
        return
    elif l == 1:
        print(requetes)
        gal = extractionGalaxies.galaxiesFiltre(requetes[0], project_path)
    else:
        print(requetes)
        gal = extractionGalaxies.galaxiesFiltreListe(requetes, project_path)

    print(gal)

    check = os.listdir(project_path + "/graphs")
    if check:
        shutil.rmtree(project_path + "/graphs")
        os.mkdir(project_path + "/graphs")
    if gal[0]:
        for num in gal[0]:
            visualisationGraphe.sauveGrapheGalaxie(num, project_path)

    check = os.listdir(project_path + "/amas")
    if check:
        shutil.rmtree(project_path + "/amas")
        os.mkdir(project_path + "/amas")
    if gal[1]:
        for numero in gal[1]:
            visualisationGraphe.sauveGrapheAmas_(numero, gal[1][numero], project_path)
