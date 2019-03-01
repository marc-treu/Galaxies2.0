#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import codecs
import parametres
import re
import baseDonnees
import sqlite3
import time
import json
import os


def lecture(fic):
    print("Appel lecture fichier sur "+str(fic))
    #FichierEntree = codecs.open(fic, 'r', 'utf-8', errors="ignore")
    connexion = sqlite3.connect(parametres.DirBD+'/galaxie.db')
    curseur = connexion.cursor()
    #Entete = FichierEntree.readline()
    #print("Entete: "+str(Entete))

    #ligne=FichierEntree.readline()
    nbre_ligne = 0
    #print("Ligne n°"+str(nbre_ligne+1)+": "+str(ligne))

    t1 = time.clock()
    for line in codecs.open(fic, 'r', 'utf-8', errors="ignore"):
        if (nbre_ligne > parametres.NombreLignes and parametres.NombreLignes != 0):
            return
        nbre_ligne += 1
        #print("Traitement ligne "+str(nbre_ligne)+": "+str(ligne))
        L=json.loads(line.rstrip())
        # i = 0
        # for item in Items:
        #     print('\t- '+ item + ': '+ L[i])
        #     i=i+1
        # baseDonnees.ajoutLivre(L[0], L[1], L[2], curseur, nbre_ligne)
        # baseDonnees.ajoutLivre(L[8], L[9], L[10], curseur, nbre_ligne)
        # #connexion.commit()
        # idSource = baseDonnees.idLivre(L[0], L[1], L[2], curseur, nbre_ligne)
        # idCible = baseDonnees.idLivre(L[8], L[9], L[10], curseur, nbre_ligne)
        # baseDonnees.ajoutReutilisation(idSource, int(L[6]), int(L[7]) - int(L[6]), L[4], idCible, int(L[14]), int(L[15])-int(L[14]), L[12], curseur, nbre_ligne)

        baseDonnees.ajoutLivre(item('source_author', L),
                               item('source_title', L),
                               itemNum('source_create_date', L), curseur, nbre_ligne)
        baseDonnees.ajoutLivre(item('target_author', L),
                               item('target_title', L),
                               itemNum('target_create_date',L), curseur, nbre_ligne)
        #connexion.commit()
        idSource = baseDonnees.idLivre(item('source_author', L),
                                       item('source_title', L),
                                       itemNum('source_create_date', L), curseur, nbre_ligne)
        idCible = baseDonnees.idLivre(item('target_author', L),
                                      item('target_title', L),
                                      itemNum('target_create_date', L), curseur, nbre_ligne)
        baseDonnees.ajoutReutilisation(idSource,
                                       int(L['source_start_byte']),
                                       int(L['source_end_byte']) - int(L['source_start_byte']),
                                       L['source_passage'],
                                       metaData(parametres.metaDataSource, L),
                                       idCible,
                                       int(L['target_start_byte']),
                                       int(L['target_end_byte'])-int(L['target_start_byte']),
                                       L['target_passage'],
                                       metaData(parametres.metaDataCible, L),
                                       curseur, nbre_ligne)
        #connexion.commit()
        if divmod(nbre_ligne, parametres.pasTracage)[1]==0:
            t2 = time.clock()
            print(" - " + str(nbre_ligne) + " réutilisations déjà traitées en un temps de "+format(t2-t1,'f')+" secondes")
            t1 = time.clock()
        #ligne=FichierEntree.readline()
    print(str(nbre_ligne) + " réutilisations dans le fichier")
    #FichierEntree.close()
    connexion.commit()
    connexion.close()

def item(Clef, L):
    if Clef in L.keys():
        return L[Clef]
    else:
        return "Inconnu"

def itemNum(Clef, L):
    if Clef in L.keys():
        return L[Clef]
    else:
        return 0


def clefsFichier(Fic):
    FichierEntree = codecs.open(Fic, 'r', 'utf-8')
    L=json.loads(FichierEntree.readline()[0:-1])
    print(L.keys())

def presenceClef(Clef, Fic)    :
    FichierEntree = codecs.open(Fic, 'r', 'utf-8')
    L = FichierEntree.readline()
    nligne = 0
    liste_lignes=[]
    while L != "":
        nligne+=1
        if not Clef in json.loads(L[0:-1]).keys():
            liste_lignes.append((nligne))
            print("Absence clef \'"+Clef+"\' sur ligne n°"+str(nligne))
        if nligne.__mod__(100000)==0:
            print("\tNombre lignes explorées "+str(nligne))
        L = FichierEntree.readline()
    print(liste_lignes)
    FichierEntree.close()


def fichierNonCache(L):
    if L == 0 or not L:
        print("Il n'y a pas de fichier de ressources!")
        return
    elif L[0][0] == '.':
        return fichierNonCache(L[1:])
    elif os.path.isfile(L[0]):
        return L[0]
    else:
        return fichierNonCache(L[1:])

def rechercheDossiersBDsAmasetGraphes(D):
    if not 'BDs' in os.listdir(D):
        os.makedirs(D+"BDs")
    if not 'amas' in os.listdir(D):
        os.makedirs(D+"amas")
    if not 'graphes' in os.listdir(D):
        os.makedirs(D+"graphes")


def metaData(clef, dict):
    if clef in dict.keys():
        return dict[clef]
    else:
        return ''
