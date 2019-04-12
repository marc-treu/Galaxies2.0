#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import baseDonnees
import grapheGalaxies
import InterfaceGalaxies
import lecture_fic
import os
import parametres

import extractionGalaxies
import time
import visualisationGraphe
import amas
import shelve

import igraph as ig
import networkx as nx
import community as louvain
import Interface
import javaVisualisation
import shutil
import re


def lancement_programme(file,maxNoeud=0):
    init_dossiers() # creation des dossiers pour stocker les données
    if not 'galaxie.db' in os.listdir(parametres.DirBD): # Si on a pas de bases de donnée
        t1 = time.clock()
        baseDonnees.creerBD()                            # On creer la Base de donnée
        t2 = time.clock()
        print("Temps de construction de la base de données: "+format(t2 - t1,'f')+" sec.")
        t1 = time.clock()
        lecture_fic.lecture(file)                     # On remplie notre BD avec notre fichiers .tab
        t2 = time.clock()
        print("Temps de lecture du fichier source: " + format(t2 - t1,'f') + " sec.")
    print("premier line de la BD = ",grapheGalaxies.grapheConstruit())
    if grapheGalaxies.grapheConstruit()!= None: # On teste si le graphe est construit
        print("Graphe déjà construit")
    else:                                       # Sinon on le construit
        maxNoeud = grapheGalaxies.construction_graphe()
        grapheGalaxies.sauvegarde_graphe_()     # Et on le sauvegarde
    if extractionGalaxies.composantesExtraites() != None:
        print("Composantes déjà extraites")
    else:
        if maxNoeud == 0:
            maxNoeud= baseDonnees.maxNoeuds()
        t1 = time.clock()
        extractionGalaxies.extractionComposantesConnexes_(maxNoeud)
        t2 = time.clock()
        print("Temps total d'extraction des composantes connexes: " + format(t2 - t1,'f') + " sec.")

def init_dossiers():
    """
    initialise la creation des dossiers pour recuperer les informations
    """
    LS = os.listdir(parametres.DirGlobal)
    if not 'BDs' in LS:
        os.mkdir(parametres.DirBD)
    if not 'graphes' in LS:
        os.mkdir(parametres.DirGraphes)
    if not 'amas' in LS:
        os.mkdir(parametres.DirAmas)
    if not 'jsons' in LS:
        os.mkdir(parametres.DirJson)
    if 'galaxie.db' in os.listdir(parametres.DirBD):
        E = input("Il y a déjà une base de données. Voulez-vous la reconstruire? (O, oui, Y, yes) ") #Ariane: raw_input
        if str.lower(E) in ['oui', 'o', 'y', 'yes']:
            baseDonnees.detruireBD()

def extractionComposantes():
    maxNoeud = baseDonnees.maxNoeuds()
    t1 = time.clock()
    extractionGalaxies.extractionComposantesConnexes_(maxNoeud)
    t2 = time.clock()
    print("Temps total d'extraction des composantes connexes: " + format(t2 - t1,'f') + " sec.")

def construction_galaxies():
    baseDonnees.detruireListeGalaxiesBD()
    maxNoeud = baseDonnees.maxNoeuds()
    t1 = time.clock()
    extractionGalaxies.extractionComposantesConnexes_(maxNoeud)
    t2 = time.clock()
    print("Temps total d'extraction des composantes connexes: " + format(t2 - t1,'f') + " sec.")

def impressionTexteEtReference(n, p):
    print("Composante "+str(n))
    q = p
    L = extractionGalaxies.textesEtReferencesGalaxie(n)
    while L != set() and (q > 0 or p == 0):
        E = L.pop()
        print("- "+str(E[0])+"\nRéférences: "+str(E[1]))
        q -= 1

def impressionTexteEtReferenceAnciennete(n, p):
    print("Composante "+str(n))
    q = p
    L = sorted(extractionGalaxies.textesEtReferencesGalaxie(n), key=lambda reference: str(reference[1][2]))
    while L != [] and (q > 0 or p == 0):
        E = L[0]
        L = L[1:]
        print("- "+str(E[0])+"\nRéférences: "+str(E[1]))
        q -= 1

def impressionTexteEtReferenceLongueur(n, p):
    print("Composante "+str(n))
    q = p
    L = sorted(extractionGalaxies.textesEtReferencesGalaxie(n), key=lambda reference: len(reference[0]))
    while L != [] and (q > 0 or p == 0):
        E = L.pop()
        print("- "+str(E[0])+"\nRéférences: "+str(E[1]))
        q -= 1

def impressionTexte(n, p):
    print("Composante "+str(n))
    q = p
    L = extractionGalaxies.textesGalaxie(n)
    while L != set() and (q > 0 or p == 0):
        E = L.pop()
        print("- "+str(E))
        q -= 1

def impressionTexteLongueur(n, p):
    print("Composante "+str(n))
    q = p
    L = sorted(extractionGalaxies.textesGalaxie(n), key=lambda reference: len(reference))
    while L != [] and (q > 0 or p == 0):
        E = L.pop()
        print("- "+str(E))
        q -= 1

def requetesUser() :
    requetes=Interface.recupereRequete()
    l=len(requetes)
    if (l==1) :
        print(requetes)
        gal=extractionGalaxies.galaxiesFiltre(requetes[0])
    elif (l>1) :
        print(requetes)
        gal=extractionGalaxies.galaxiesFiltreListe(requetes)
    else :
        gal=[]
    print(gal)

    check = os.listdir(parametres.DirGraphes)
    if check :
        shutil.rmtree(parametres.DirGraphes)
        os.mkdir(parametres.DirGraphes)
    if gal[0] :
        for num in gal[0] :
            visualisationGraphe.sauveGrapheGalaxie(num)

    check = os.listdir(parametres.DirAmas)
    if check :
        shutil.rmtree(parametres.DirAmas)
        os.mkdir(parametres.DirAmas)
    if gal[1] :
        for numero in gal[1] :
            visualisationGraphe.sauveGrapheAmas_(numero, gal[1][numero])


if __name__ == '__main__':

    #interface = InterfaceGalaxies.InterfaceGalaxies()

    #listGraph = baseDonnees.getListeGraphe()
    #listGraph = ["Graphe "+str(i)+" de 4 noeuds" for i in range(100)]
    #interface.display_graphe_list(listGraph)
    #interface.mainloop()

    dossierCourant = os.chdir(parametres.DirFichier)
    Fichier = lecture_fic.fichierNonCache(os.listdir(parametres.DirFichier))

    start=time.clock()

    maxNoeud = 0
    lancement_programme(Fichier,maxNoeud)
    amas.recupererAmas()
    amas.requetesUser()
    print('fin requête utilisateur')
    """
    javaVisualisation.preparationVisualisation()

    fichiers=Interface.selectionAffichage()

    print(fichiers)
    if fichiers :
        for i in fichiers :
            tmp=[int(s) for s in re.findall(r'\d+', i)]
            if len(tmp)==2 :
                javaVisualisation.affichage(parametres.DirGlobal+'jsons/galaxie_'+str(tmp[0])+'.json')
            elif len(tmp)==3 :
                javaVisualisation.affichage(parametres.DirGlobal+'jsons/galaxie_'+str(tmp[1])+'_amas_'+str(tmp[0])+'.json')


    finish=time.clock()
    print('Le programme s\'est exécuté en '+format((finish - start)/60,'f')+'mn')
    """
