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
    """
    Lit le fichier fic passer en parametres et remplie la base de donnée
    fic : le resultat de text_align
    """
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
        L=json.loads(line.rstrip())

        baseDonnees.ajoutLivre(item('source_author', L),
                               item('source_title', L),
                               itemNum('source_create_date', L), curseur, nbre_ligne)
        baseDonnees.ajoutLivre(item('target_author', L),
                               item('target_title', L),
                               itemNum('target_create_date',L), curseur, nbre_ligne)
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
        if divmod(nbre_ligne, parametres.pasTracage)[1]==0: # permet de tenir au courant l'utilisateur
            t2 = time.clock()                               # du temps de construction du graphe
            print(" - " + str(nbre_ligne) + " réutilisations déjà traitées en un temps de "+format(t2-t1,'f')+" secondes")
            t1 = time.clock()
    print(str(nbre_ligne) + " réutilisations dans le fichier")
    connexion.commit()
    connexion.close()



def item(clef, dict):
    """
    Retourne la valeur de L[Clef] si elle existe, sinon Inconnu
    L : un dictionnaire
    Clef : une clef potentielle de L
    """
    return dict[clef] if clef in dict.keys() else "Inconnu"

def itemNum(clef, dict):
    """
    Retourne la valeur de L[Clef] si elle existe, sinon 0
    L : un dictionnaire
    Clef : une clef potentielle de L
    """
    return dict[clef] if clef in dict.keys() else 0

def metaData(clef, dict):
    """
    Retourne la valeur de L[Clef] si elle existe, sinon ''
    L : un dictionnaire
    Clef : une clef potentielle de L
    """
    return dict[clef] if clef in dict.keys() else ''

def fichierNonCache(L):
    """
    Fonction qui va retourné le premier fichier d'une liste
    L : List de dossiers ou de fichiers retourné par os.listdir()
    """
    # TODO: Retourner une liste de fichiers potentielle a traités, pas seulement le premier
    #       peu etre regarder tous ce qui n'est pas un dossiers et qui fini par .tab
    if L == 0 or not L:
        print("Il n'y a pas de fichier de ressources!")
        return
    elif L[0][0] == '.': # On ne se préocupe pas de ./ et de ../
        return fichierNonCache(L[1:])
    elif os.path.isfile(L[0]):
        return L[0]
    else:
        return fichierNonCache(L[1:])

#### les Fonctions dans la suite n'on pas l'aire utile

def clefsFichier(Fic): # Fonction jamais utiliser dans le reste du code
    FichierEntree = codecs.open(Fic, 'r', 'utf-8')
    L=json.loads(FichierEntree.readline()[0:-1])
    print(L.keys())

def presenceClef(Clef, Fic): # Fonction jamais utiliser dans le reste du code
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


def rechercheDossiersBDsAmasetGraphes(D): # Fonction qui crée nos dossiers BDs amas et graphe ?
    if not 'BDs' in os.listdir(D):
        os.makedirs(D+"BDs")
    if not 'amas' in os.listdir(D):
        os.makedirs(D+"amas")
    if not 'graphes' in os.listdir(D):
        os.makedirs(D+"graphes")
