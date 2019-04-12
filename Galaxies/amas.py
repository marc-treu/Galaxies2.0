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


import parametres
import visualisationGraphe
import baseDonnees
#import Interface
import extractionGalaxies

def listeAmas(numGalaxie) :
    listeAmas=shelve.open(parametres.DirBD+'/listeAmasGalaxie'+str(numGalaxie))
    if(len(listeAmas)>0) :
        E = input("Liste des amas de la galaxie "+str(numGalaxie)+" déjà remplie. Souhaitez-vous recommencer l'opération ? (O, oui, Y, yes) ")
        if str.lower(E) not in ['oui', 'o', 'y', 'yes']:
            return
    print('Récupération de la galaxie '+str(numGalaxie))
    td=time.clock()
    fichierGrapheGalaxie = visualisationGraphe.sauveGrapheGalaxie(numGalaxie)
    tf=time.clock()
    print('Galaxie récupérée en '+format(tf - td,'f')+'s'+ "- sauvegardée dan "+fichierGrapheGalaxie)

    #fichierGrapheGalaxie = parametres.DirGraphes+'/graphe_galaxie_TC_'+str(numGalaxie)+'.gexf'
    gr=nx.read_gexf(fichierGrapheGalaxie)
    print('Création de la partition de la galaxie')
    td=time.clock()
    amas=louvain.best_partition(gr)
    tf=time.clock()
    print('Partition de '+str(len(amas))+' nœuds créée en '+format(tf - td,'f')+'s')
    liste_Amas = dict()
    for x in amas:
        if amas[x] in liste_Amas.keys():
            liste_Amas[amas[x]].append(x)
        else:
            liste_Amas[amas[x]]=[x]
    for a in liste_Amas:
        listeAmas[str(a)]=liste_Amas[a]
    #print("Liste des amas: ",liste_Amas)
    #for a in c
    # res=[[] for i in range(len(amas))]
    # p=False
    # sub=False
    # k=0
    # print('Inscription des amas dans le fichier shelve')
    # TD=time.clock()
    # for k in range(len(amas)):
    #     i=0
    #     td=time.clock()
    #     for i in range(len(amas[k])):
    #         if(i> parametres.tailleMinGrosseGalaxie) and not p :
    #             p = True
    #             sub = Interface.subSort()
    #         res[k].insert(i, gr.vs[amas[k][i]]['label'])
    #     listeAmas[str(k)]=res[k]
    #     tf=time.clock()
    #     print('amas '+str(k)+' de '+str(len(amas[k]))+' noeuds ajouté en '+format(tf - td,'f')+'s')
    # TF=time.clock()
    #print('Fichier shelve rempli en '+format(TF - TD,'f')+'s')
    os.remove(fichierGrapheGalaxie)#parametres.DirGraphes+'/graphe_galaxie_TC_'+str(numGalaxie)+'.gml')
    listeAmas.close()

def recupererAmas():
    noeudsGalaxies=shelve.open(parametres.DirBD + '/listeGalaxies')
    j=0
    td=time.clock()
    # print(len(noeudsGalaxies))
    while j<baseDonnees.nombreGalaxies()-1:
        if len(noeudsGalaxies[str(j)])>parametres.tailleMinGrosseGalaxie :
            print('Galaxie numéro '+str(j)+' de taille '+str(len(noeudsGalaxies[str(j)]))+'\nAppel de Louvain')
            noeudsGalaxies.close()
            listeAmas(j)
            noeudsGalaxies=shelve.open(parametres.DirBD + '/listeGalaxies')

            # i=i+1
        # elif len(noeudsGalaxies[str(j)])>4 :
            # visualisationGraphe.sauveGrapheGalaxie(j)
        j += 1
    tf=time.clock()
    if(tf-td<60) :
        print ('Amas extraits en '+format(tf-td, 'f')+'s')
    elif(tf-td<3600) :
        print ('Amas extraits en '+format((tf - td)/60,'f')+'mn')
    else :
        print ('Amas extraits en '+format((tf - td)/3600,'f')+'h')
    noeudsGalaxies.close()

# def requetesUser() :
#     print("Appel requête utilisateur")
#     ###requetes = Interface.recupereRequete()
#     requête = {} ## Don't use this fonction, because Interface no longer exist
#     l=len(requetes)
#     if (l==0):
#         return
#     elif (l==1) :
#         print(requetes)
#         gal=extractionGalaxies.galaxiesFiltre(requetes[0])
#     else:
#         print(requetes)
#         gal=extractionGalaxies.galaxiesFiltreListe(requetes)
#
#     print(gal)
#
#     check = os.listdir(parametres.DirGraphes)
#     if check :
#         shutil.rmtree(parametres.DirGraphes)
#         os.mkdir(parametres.DirGraphes)
#     if gal[0] :
#         for num in gal[0] :
#             visualisationGraphe.sauveGrapheGalaxie(num)
#
#     check = os.listdir(parametres.DirAmas)
#     if check :
#         shutil.rmtree(parametres.DirAmas)
#         os.mkdir(parametres.DirAmas)
#     if gal[1] :
#         for numero in gal[1] :
#             visualisationGraphe.sauveGrapheAmas_(numero, gal[1][numero])

def requetesUser(requetes):
    l=len(requetes)
    if (l==0):
        return
    elif (l==1) :
        print(requetes)
        gal=extractionGalaxies.galaxiesFiltre(requetes[0])
    else:
        print(requetes)
        gal=extractionGalaxies.galaxiesFiltreListe(requetes)

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
