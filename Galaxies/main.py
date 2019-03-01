#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import os
import parametres
import lecture_fic
import baseDonnees
import grapheGalaxies

import extractionGalaxies
import time
# import filtres
import visualisationGraphe
# import subprocess
import amas
import shelve

# import sys
# import cProfile
# import random
# import array

import igraph as ig
import networkx as nx
import community as louvain
#import louvain
import Interface
import javaVisualisation
import shutil
import re
# from tkinter import *
# from tkinter.messagebox import *
# import networkx as nx
# import matplotlib.pyplot as plt
# import json



dossierCourant = os.chdir(parametres.DirFichier)
# print(dossierCourant)
Fichier = lecture_fic.fichierNonCache(os.listdir(parametres.DirFichier))



#Fichier = os.listdir(dossierCourant)[0]
maxNoeud = 0


# maxNoeud= baseDonnees.maxNoeuds()
# print("Max Noeud: "+str(maxNoeud))
# t1 = time.clock()
#     #cProfile.run('extractionGalaxies.extractionComposantesConnexes(maxNoeud)')
# G = extractionGalaxies.extractionComposantesConnexes(maxNoeud)
# t2 = time.clock()
# print("Temps total d'extraction des composantes connexes: " + str(t2 - t1) + "sec. - nombre galaxies extraites: "+ str(G.valeur()))
# for i in range(1, 100):
#     print("Galaxie i="+str(i)+" = "+str(G.compositionGalaxie[i]))
# print(G.val)
# L = G.compositionGalaxie.keys()
# for i in range(1, 30):
#     print("Galaxie numéro: "+str(i)+" - contenu: "+str(G.compositionGalaxie[i])+" longueur: "+str(len(G.compositionGalaxie[i])))
# G.sauvegarde()
# for X in extractionGalaxies.textesGalaxie(18):
#     print("- ", str(X))
#
# for X in extractionGalaxies.textesEtReferencesGalaxie(17):
#     print("- ", str(X[0])+" - Auteur: "+str(X[1][0])+" - titre: "+str(X[1][1])+" - année: "+str(X[1][2]))
# n = extractionGalaxies.extractionComposantesConnexes(maxNoeud)

# graphe = shelve.open(parametres.DirBD + '/liste_ajacence_graphe')
# graphe_t = shelve.open(parametres.DirBD + '/liste_ajacence_graphe_transpose')
# g = extractionGalaxies.galaxie()
# n = extractionGalaxies.noeudMarques(maxNoeud)
# for i in range(0,maxNoeud):
#     L = extractionGalaxies.fils(i, graphe, graphe_t)
#     print("Fils de "+str(i)+": "+str(L))
#     LC = extractionGalaxies.composanteConnexe(i, g, graphe, graphe_t, n)
#     print("composante connexe de "+str(i)+":"+str(LC))
# g = extractionGalaxies.galaxie()
# n = extractionGalaxies.noeudMarques(maxNoeud)
#
# for i in range(0, 9):
#     j = n.noeudNonVisite(i)
#     print("Valeur de galaxie de "+str(i)+": "+str(j))
#     k = j
#     while k < j*2+1:
#         if n.noeuds[k] != 'non':
#             print("mauvaise initialisation pour k = "+str(k)+":"+str(n.noeuds(k)))
#         n.affectationGalaxie(k, g)
#         print("Valeur de noeuds["+str(k)+"] après l'affectation: "+str(n.noeuds[k]))
#         k += 1
#     g.nouvelleValeur()
#
# print("Nombre de galaxies: "+str(g.val)+"; rand du premier noeud non affecté: "+str(n.noeudNonVisite(1)))
#
#
#
#



# for i in range(0, 100):
#     g.nouvelleValeur()
#     k = n.noeudNonVisite(i)
#     for j in [k, 3*k]:
#         n.affectationGalaxie(str(j), g)

# A = set([1, 2, 3])
# print(A)
# A.update([0,4])
# print(A)
# B = A.pop()
# print(B)
# print(A)
# B = A.difference({0,4})
# print(A)
# print(B)
#

def lancement_programme(maxNoeud):
    init_dossiers()
    if not 'galaxie.db' in os.listdir(parametres.DirBD):
        t1 = time.clock()
        baseDonnees.creerBD()
        t2 = time.clock()
        print("Temps de construction de la base de données: "+format(t2 - t1,'f')+" sec.")
        t1 = time.clock()
        #cProfile.run('lecture_fic.lecture(Fichier)')
        lecture_fic.lecture(Fichier)
        t2 = time.clock()
        print("Temps de lecture du fichier source: " + format(t2 - t1,'f') + " sec.")
    if grapheGalaxies.grapheConstruit()!= None:
        print("Graphe déjà construit")
    else:
        #cProfile.run('maxNoeud = grapheGalaxies.construction_graphe()')
        maxNoeud = grapheGalaxies.construction_graphe()
        #cProfile.run('grapheGalaxies.sauvegarde_graphe()')
        grapheGalaxies.sauvegarde_graphe_()
    if extractionGalaxies.composantesExtraites() != None:
        print("Composantes déjà extraites")
    else:
        if maxNoeud == 0:
            maxNoeud= baseDonnees.maxNoeuds()
        t1 = time.clock()
        #cProfile.run('extractionGalaxies.extractionComposantesConnexes_(maxNoeud)')
        extractionGalaxies.extractionComposantesConnexes_(maxNoeud)
        t2 = time.clock()
        print("Temps total d'extraction des composantes connexes: " + format(t2 - t1,'f') + " sec.")

def init_dossiers():
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
    # cProfile.run('extractionGalaxies.extractionComposantesConnexes(maxNoeud)')
    extractionGalaxies.extractionComposantesConnexes_(maxNoeud)
    t2 = time.clock()
    print("Temps total d'extraction des composantes connexes: " + format(t2 - t1,'f') + " sec.")

def construction_galaxies():
    baseDonnees.detruireListeGalaxiesBD()
    maxNoeud = baseDonnees.maxNoeuds()
    t1 = time.clock()
    #cProfile.run('extractionGalaxies.extractionComposantesConnexes_(maxNoeud)')
    extractionGalaxies.extractionComposantesConnexes_(maxNoeud)
    t2 = time.clock()
    print("Temps total d'extraction des composantes connexes: " + format(t2 - t1,'f') + " sec.")

def impressionTexteEtReference(n, p):
    print("Composante "+str(n))
    q = p
    L = extractionGalaxies.textesEtReferencesGalaxie(n)
    #print(L)
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

#L=extractionGalaxies.galaxiesTitreMot('Madame')
#print(L)
#L=extractionGalaxies.galaxiesAuteur('Rousseau')
#print(L)
#LL = extractionGalaxies.ordonner(L)
#print(LL)
# L=extractionGalaxies.galaxiesAuteurOrdonnees('Marmontel')
# print(L)
#lecture_fic.nouvLecture(Fichier)
#L=extractionGalaxies.textesEtReferencesGalaxie(0)
#print(L)
# requete = {'nbre_minimal_noeuds':5, 'longueur_texte_maximal':500}
#A=amas.constructionAmas(0)
# A.filtrageAmas(requete)
#print(baseDonnees.reutilisations(23))
#print("Groupes : ",list(A.groupe.keys()))
#visualisationGraphe.sauveGrapheGalaxie(84)

#visualisationGraphe.sauveGrapheGalaxieTC(8407)
#2092, 2096, 8407, 19449

#L=extractionGalaxies.galaxiesAuteur('Voltaire')
# L=extractionGalaxies.galaxiesNomsAuteurOrdonnees(['Jean-Jacques', 'Rousseau'])
# print("Jean-Jacques Rousseau"+str(L))
# L=extractionGalaxies.galaxiesAuteurOrdonnees('Jean-Jacques')
# print("Jean-Jacques"+str(L))
# L = extractionGalaxies.galaxiesListesNomsAuteurs([['Jean-Jacques', 'Rousseau'], ['Voltaire']])
# print(L)
#print(L)
#print(extractionGalaxies.auteursGalaxie(5034))
#os.system('gnome-terminal')
# Galaxies intéressantes: 822,1, 11907
#impressionTexteEtReferenceLongueur(2452,20)
#impressionTexteEtReferenceLongueur(578, 0)
#impressionTexteEtReferenceLongueur(1760,0)
#impressionTexteEtReferenceLongueur(2092, 0)
#impressionTexteEtReferenceLongueur(2096,0)
#impressionTexteEtReferenceLongueur(8407, 0)
#impressionTexteEtReferenceLongueur(19449,0)

#impressionTexteEtReferenceAnciennete(34, 50)
#A = amas.constructionAmas(0)
#A = amas.constructionAmas(5363) # pire des cas...
#A = amas.constructionAmas(121505)
#A = amas.constructionAmas(36415)
#A.impression_groupes_degre()
#A.impression_groupes_degre()

#A.impression_tous_groupes_anciennete(5)
#amas.ficherGalaxie(14640)
# graphText = parametres.DirAmas+"/galaxie_graphe.txt"
# graphBin = parametres.DirAmas + '/galaxie_graphe.bin'
# graphTree = parametres.DirAmas + '/galaxie_graphe.tree'
#fic=open('/Users/jean-gabriel/Desktop/GalaxieBDs/amas/galaxie_graphe.tree',mode='wt')
#L = subprocess.Popen([parametres.DirLouvain+'/./louvain', graphBin, '-l -1 -q id_qual >'], shell=True, stdout=subprocess.PIPE)
#subprocess.Popen(parametres.DirLouvain+'/./louvain /Users/jean-gabriel/Desktop/GalaxieBDs/amas/galaxie_graphe.bin -l -1 -q id_qual > /Users/jean-gabriel/Desktop/GalaxieBDs/amas/galaxie_graphe.tree', shell=True)
#subprocess.run('more '+graphText+' > '+graphTree, shell=True)
# os.chdir(parametres.DirLouvain)
# subprocess.run('./louvain '+graphBin+' -l -1 -q id_qual > '+graphTree, shell=True)

#fic.close()
#subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None)

# L=extractionGalaxies.chaineMax(616610, 36, "ville, située dans la partie la plus", 616625, 28,"dans la partie la plus large")
# print(L)
# # L = extractionGalaxies.chaineMax(698950, 34, "dans sa chambre au coin de son feu", 698908, 65,
# #                                  "lui disait être imaginaires. Elle était dans sa chambre au coin")
# # print(L)
# L = extractionGalaxies.chaineMax(698948, 34, "dans sa chambre au coin de son feu", 698910, 63,
#                                  "lui disait être imaginaires. Elle était dans sa chambre au coin")
# print(L)
#
# L = extractionGalaxies.chaineMax(12800, 52, "eût pas donné plus de trente années, tant il y avait", 12803, 56,
#                                   "lui eût pas donné plus de trente années, tant il y avait")
# print(L)
#lancement_programme()

# requete = {'auteur':['d\'Holbach'], 'empan':100, 'date':[1800,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - d\'Holbach", L)

# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':100,  'date':[1800,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau ", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':100,  'date':[1800,'-'], 'mots_tire': ['contrat', 'social'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau ", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':100,  'date':[1800,'-'], 'target_subject':'littérature', 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau ", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':100,  'date':[1800,'-'], 'target_subject':'politique', 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau ", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':100,  'date':[1800,'-'], 'target_subject':'philosophie', 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau ", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':300,  'date':[1800,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau ", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':300,  'date':[1800,'-'], 'mots_tire': ['contrat', 'social'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau contrat social", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':300,  'date':[1800,'-'], 'target_subject':'littérature', 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau littérature", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':300,  'date':[1800,'-'], 'target_subject':'politique', 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau politique", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':300,  'date':[1800,'-'], 'target_subject':'philosophie', 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau ", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':300,  'date':[1800,'-'], 'target_subject':'littérature','mots_titre':['contrat', 'social'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau ", L)

# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':100,  'mots_titre':['Emile', 'éducation'], 'nbre_minimal_noeuds':50, 'longueur_texte_maximal':300}
# requete0 = {'date':[1800,'-']}
#
# requete1 = {'auteur':['Proudhon'], 'empan':100, 'date':[1820,'-'], 'nbre_minimal_noeuds':2, 'longueur_texte_maximal':500}
# requete2 = {'auteur':['Rousseau'], 'empan':100, 'target_subject':'Politique', 'nbre_minimal_noeuds':2, 'longueur_texte_maximal':500}
# requete3 = {'auteur':['Rousseau'], 'empan':100, 'nbre_minimal_noeuds':2, 'longueur_texte_maximal':500}
# Lrequetes = [requete0, requete3]
#print("Proudhon: ", L1, "; Rousseau: ", L2, " - ", set(L1).intersection(set(L2)))
#L1 = extractionGalaxies.galaxiesFiltre(requete)
#print("Auteur - Rousseau contrat social - philosophie", L1)

# A=amas.constructionAmas(0)
#A.filtrageAffichageAmasListe([requete0, requete2])
#A.filtrageAffichageAmasListe([requete0, requete3])
# A.filtrageAffichageAmasListe([requete0, requete])
# R = filtres.choixRequete([requete1, requete2, requete0])
# print("Résultat: ", R)
# requete = {'date':[1800,'-']}
#extractionGalaxies.galaxiesFiltreListeAffiche(Lrequetes)
#visualisationGraphe.sauveGrapheGalaxieFiltre(requete, 168)
# requete = {'auteur':['J.-J.', 'Rousseau'], 'empan':200,  'date':[1800,'-'], 'mots_titre':['contrat'], 'target_subject':'philosophie', 'nbre_minimal_noeuds':3, 'longueur_texte_maximal':200}
# L2 = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - J.-J. Rousseau contrat social - philosophie", L2)
#
# requete = {'auteur':['Rousseau'], 'empan':200, 'target_subject':'littérature',  'mots_titre':['contrat'], 'nbre_minimal_noeuds':3, 'longueur_texte_maximal':200}
# L2 = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - J.-J. Rousseau contrat social - philosophie", L2)
#
# visualisationGraphe.sauveGrapheGalaxie(22414)
# visualisationGraphe.sauveGrapheGalaxie(22418)
# visualisationGraphe.sauveGrapheGalaxie(12353)

# baseDonnees.valeursMetaDataCible()
# baseDonnees.valeursMetaDataSource()

# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'mots_titre': ['Contrat', 'Social'], 'empan':100,  'date':[1800,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau - livre Contrat Social ", L)

# requete = {'auteur':['d\'Holbach'], 'empan':100, 'date':[1800,'-'],  'target_birth':[1765,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - d\'Holbach auteur nés après 1765", L)

# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':100, 'target_birth':[1765,'-'], 'date':[1800,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau - livre Contrat Social auteur nés après 1765", L)

# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'mots_titre': ['Contrat', 'Social'], 'empan':100, 'target_birth':[1765,'-'], 'date':[1800,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau - livre Contrat Social auteur nés après 1765", L)

# requete = {'auteur':['d\'Holbach'], 'empan':100, 'date':[1800,'-'], 'target_birth':[1765,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - d\'Holbach", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'empan':100, 'date':[1800,'-'], 'target_birth':[1765,'-'],'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau", L)
#
# requete = {'auteur':['Jean-Jacques', 'Rousseau'], 'mots_titre': ['Contrat', 'Social'], 'empan':100, 'target_birth':[1765,'-'], 'date':[1800,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - Rousseau - livre Contrat Social", L)
#
#
# requete = {'auteur':['d\'Holbach', 'Diderot'], 'empan':100, 'date':[1800,'-'],'target_birth':[1765,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Auteur - d\'Holbach et Diderot", L)
#

# requete = {'source_generatedclass':'Jurisprudence', 'empan':100, 'date':[1800,'-'],'target_birth':[1765,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Jurisprudence après 1800: ", L)
#
# requete = {'source_generatedclass':'Morale', 'empan':100, 'date':[1800,'-'],'target_birth':[1765,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Morale après 1800: ", L)
#
# requete = {'source_generatedclass':'Belles-Lettres', 'empan':100, 'date':[1800,'-'],'target_birth':[1765,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Belles-Lettres après 1800: ", L)

# requete = {'source_generatedclass':'Métaphysique', 'empan':100, 'date':[1800,'-'], 'target_birth':[1765,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Métaphysique après 1800: ", L)
#
# requete = {'source_generatedclass':'Littérature', 'empan':100, 'date':[1800,'-'], 'target_birth':[1765,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Littérature après 1800: ", L, len(L))

# requete = {'source_generatedclass':'Mythologie', 'empan':100, 'date':[1800,'-'], 'target_birth':[1765,'-'], 'nbre_minimal_noeuds':4, 'longueur_texte_maximal':500}
# L = extractionGalaxies.galaxiesFiltre(requete)
# print("Mythologie après 1800: ", L, len(L))



#Texte ancien: [("temps que l'Empire, mais sa veuve trouvaquinze mille francs de rentes dansinze mille francs de rentes dans", 10463, 75)] - texte nouveau: ("trouva quinze mille francs de rentes dans",10497, 41) jointure: temps que l'Empire, mais sa veuve trouvaquinze mille francs de rentes dansinze mille francs de rentes dansouva quinze mille francs de rentes dans
#Texte ancien: [('pourra valoir, un jour, près de quinze mille francs de rente', 366391, 61)] - texte nouveau: ("près de quinze mille francs de rente",366415, 37) jointure: pourra valoir, un jour, près de quinze mille francs de renteès de quinze mille francs de rente
#(, )] - texte nouveau: (,) jointure: eus environ quinze mille francs de rentesn tout. Cette fortune
# subprocess.run('pwd')

#print(Fichier)
#extractionComposantes()
#lecture_fic.clefsFichier(Fichier)
#lancement_programme()
#lecture_fic.presenceClef('source_author', Fichier)
# construction_galaxies()
# def essai(n):
#     while n > 0:
#         s2 = {4, 5, 6}
#         s1 = {7, 8, 6, 9, 10, 11,12, 13, 15, 18, 19, 20, 21, 22, 23}
#         s = s1 - s2
#         n = n-1
#     return
#cProfile.run('essai(1000000)')

# print("Composante 127")
# for X in extractionGalaxies.textesEtReferencesGalaxie(127):
#     print("- "+X[0]+" références: "+str(X[1]))
#
# print("Composante 179")
# for X in extractionGalaxies.textesEtReferencesGalaxie(179):
#     print("- " + X[0]+" références: "+str(X[1]))
#
# print("Composante 63")
# for X in extractionGalaxies.textesGalaxie(63):
#     print("- "+X)
#
# print("Composante 67")
# for X in extractionGalaxies.textesGalaxie(67):
#     print("- " + X)
#
# print("Composante 973")
# for X in extractionGalaxies.textesGalaxie(307):
#     print("- " + X)
#
#
# gr=ig.Graph.Read_GML("/local/raviera/Galaxies/graphesGML-encyclopedie/Graphe190.gml")

# data=json.load(open('/local/raviera/Galaxies/balzac/graphes/Graphe09.json'))
# print(data['edges'][2])

# td=time.clock()
# gr=ig.read("/local/raviera/Galaxies/balzac/graphes/Graphe09.gml", format="gml")
# tf=time.clock()
# print('Fichier GML lu en '+format(tf - td,'f')+'s')
# print(str(gr.vcount())+' noeuds et '+str(gr.ecount())+' arêtes')
# td=time.clock()
# amas=louvain.find_partition(gr, louvain.ModularityVertexPartition)
# tf=time.clock()
# print('Partition créée en '+format(tf - td,'f')+'s')

# remplacer le chemin par parametres.DirBD+nomfichier.gml
# MAIS cela implique de générer les graphes en format GML
# ig.summary(gr)
# k=0
# while k < gr.vcount() :
#     gr.vs[k]['texte']=gr.vs[k]['texte'].decode('utf-8')
#     gr.vs[k]['titre']=gr.vs[k]['titre'].decode('utf-8')
#     gr.vs[k]['auteur']=gr.vs[k]['auteur'].decode('utf-8')
#     k=k+1

# print(gr.vs[24]['texte'])
# print(gr.vs[24])
# td=time.clock()
# amas=louvain.find_partition(gr, louvain.ModularityVertexPartition)
# tf=time.clock()
# print('Partition créée en '+format(tf - td,'f')+'s')


# def listeAmas(galaxie, numGalaxie) :
#     listeAmas=shelve.open(parametres.DirBD+'/listeAmasGalaxie'+str(numGalaxie))
#     if(len(listeAmas)>0) :
#         E = input("Liste des amas de la galaxie "+str(numGalaxie)+" déjà remplie. Souhaitez-vous recommencer l'opération ? (O, oui, Y, yes) ")
#         if str.lower(E) not in ['oui', 'o', 'y', 'yes']:
#             return
#     print('Récupération de la galaxie '+str(numGalaxie))
#     td=time.clock()
#     visualisationGraphe.sauveGrapheGalaxie(numGalaxie)
#     #visualisationGraphe.sauveGrapheGalaxieGML(numGalaxie)
#     tf=time.clock()
#     print('Galaxie récupérée en '+format(tf - td,'f')+'s')
#     gr=nx.read_gexf(parametres.DirGraphes+'/graphe_galaxie_TC_'+str(numGalaxie)+'.gexf')#, format="gml")
#     print('Création de la partition des amas')
#     td=time.clock()
#     amas=louvain.best_partition(gr)
#     tf=time.clock()
#     print('Partition de '+str(len(amas))+' nœuds créée en '+format(tf - td,'f')+'s')
#     print(amas)
#     res=[[] for i in range(len(amas))]
#     p=False
#     sub=False
#     k=0
#     print('Inscription des amas dans le fichier shelve')
#     TD=time.clock()
#     for k in range(len(amas)):
#         i=0
#         td=time.clock()
#         for i in range(len(amas[k])):
#             if(i> parametres.tailleMinGrosseGalaxie) and not p :
#                 p = True
#                 sub = Interface.subSort()
#             res[k].insert(i, gr.vs[amas[k][i]]['label'])
#         listeAmas[str(k)]=res[k]
#         tf=time.clock()
#         print('amas '+str(k)+' de '+str(len(amas[k]))+' noeuds ajouté en '+format(tf - td,'f')+'s')
#     TF=time.clock()
#     print('Fichier shelve rempli en '+format(TF - TD,'f')+'s')
#     os.remove(parametres.DirGraphes+'/graphe_galaxie_TC_'+str(numGalaxie)+'.gml')
#     listeAmas.close()
#
# def recupererAmas():
#     noeudsGalaxies=shelve.open(parametres.DirBD + '/listeGalaxies')
#     j=0
#     td=time.clock()
#     # print(len(noeudsGalaxies))
#     while j<baseDonnees.nombreGalaxies()-1:
#         if len(noeudsGalaxies[str(j)])>parametres.tailleMinGrosseGalaxie :
#             print('Galaxie numéro '+str(j)+' de taille '+str(len(noeudsGalaxies[str(j)]))+'\nAppel de Louvain')
#             listeAmas(noeudsGalaxies[str(j)],j)
#             # i=i+1
#         # elif len(noeudsGalaxies[str(j)])>4 :
#             # visualisationGraphe.sauveGrapheGalaxie(j)
#         j += 1
#     tf=time.clock()
#     if(tf-td<60) :
#         print ('Amas extraits en '+format(tf-td, 'f')+'s')
#     elif(tf-td<3600) :
#         print ('Amas extraits en '+format((tf - td)/60,'f')+'mn')
#     else :
#         print ('Amas extraits en '+format((tf - td)/3600,'f')+'h')
#     noeudsGalaxies.close()

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


start=time.clock()

maxNoeud = 0
#print(fichier)
lancement_programme(maxNoeud)
amas.recupererAmas()
amas.requetesUser()
print('fin requête utilisateur')
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
