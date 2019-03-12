#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'


import sqlite3
import shelve
import re
import os
import parametres
import time

import igraph as ig
import community as louvain

def creerBD():
    if not 'galaxie.db' in os.listdir(parametres.DirBD):
        print("Création de la base de données 'galaxie.db'")
        connexion = sqlite3.connect(parametres.DirBD+'/galaxie.db', 1, 0, 'EXCLUSIVE')
        curseur = connexion.cursor()
        curseur.execute('''CREATE TABLE livres (idLivre TEXT UNIQUE, auteur TEXT, titre TEXT, date INTEGER)''')
        curseur.execute('''CREATE TABLE grapheReutilisations (idRefSource TEXT, ordonneeSource INTEGER, empanSource INTEGER, texteSource TEXT, metaDataSource TEXT, idRefCible TEXT, ordonneeCible INTEGER, empanCible INTEGER, texteCible TEXT, metaDataCible TEXT)''')
        curseur.execute('''CREATE TABLE grapheGalaxiesSource (idReutilisation INTEGER UNIQUE, idNoeud INTEGER)''')
        curseur.execute('''CREATE TABLE grapheGalaxiesCible (idReutilisation INTEGER UNIQUE, idNoeud INTEGER)''')
        curseur.execute('''CREATE TABLE grapheGalaxies (idNoeudPere INTEGER, idNoeudFils INTEGER)''')
        curseur.execute('''CREATE TABLE texteNoeuds (idNoeud INTEGER UNIQUE, texte TEXT, idRowLivre INTEGER, ordonnee INTEGER, empan INTEGER)''')
        curseur.execute('''CREATE TABLE maxNoeud (idNoeud INTEGER)''')
        curseur.execute('''CREATE TABLE nombreGalaxies (nbre INTEGER)''')
        curseur.execute('''CREATE TABLE degreGalaxies (idGalaxie INTEGER UNIQUE, degreGalaxie INTEGER, longueurTexteTotale INTEGER, longueurTexteMoyenne INTEGER, longueurTexteMax INTEGER)''')
        curseur.execute('''CREATE INDEX idLivreSource ON grapheGalaxiesSource (idNoeud)''')
        curseur.execute('''CREATE INDEX idLivreCible ON grapheGalaxiesCible (idNoeud)''')
        curseur.execute('''CREATE INDEX refSource ON grapheReutilisations (idRefSource)''')
        curseur.execute('''CREATE INDEX refCible ON grapheReutilisations (idRefCible)''')
        curseur.execute('''CREATE INDEX idNoeud ON grapheGalaxies (idNoeudPere)''')
        curseur.execute('''CREATE INDEX idNoeudf ON grapheGalaxies (idNoeudFils)''')
        curseur.execute('''CREATE INDEX identifiantNoeud ON texteNoeuds (idNoeud)''')
        # curseur.execute('''CREATE INDEX dateIndex ON livres (date) ASC''')
        # curseur.execute('''CREATE INDEX idReutSource ON grapheGalaxiesSource (idReutilisation)''')
        # curseur.execute('''CREATE INDEX idReutCible ON grapheGalaxiesCible (idReutilisation)''')
        #
        # curseur.execute('''CREATE INDEX refLivre ON livres (idLivre)''')

        curseur.close()


def dateToInt(date):
    # print(date)
    # if not date or date=='' or date=='....':
    #     return ''
    if type(date) == type(0):
        return normalisation_date(date)
    d=date.encode('ascii', 'ignore')
    #print(d)
    tmp=''
    for x in filter(str.isdigit,str(d)):
        tmp = tmp+x
    #print(type(tmp))
    if not tmp:
        return 0 # correction '' remplacé par 0
    if len(tmp)>4 :
        tmp=tmp[:4]
    date=int(tmp)
    return normalisation_date(date)

def normalisation_date(date):
    d = str(date)
    if len(d) == 2:
        return date * 100
    return date

def ajoutLivre(auteur, titre, date, curseur, nbre_lignes):
    t1 = time.clock()
    id = idRef(auteur, titre, date, curseur, nbre_lignes)
    curseur.execute('''SELECT * FROM livres WHERE idLivre = ?''', (id,))
    L = curseur.fetchone()
    if not L:
        date=dateToInt(date)
        curseur.execute('''INSERT INTO livres values (?,?,?,?)''', (id,auteur, titre, date))
    # if divmod(nbre_lignes, parametres.pasTracage)[1]==0:
    #         t2 = time.clock()
    #         print(" temps d'insertion d'un livre "+str(t2-t1)+"secondes")



def idRef(auteur, titre, date, curseur, nbre_lignes):
    # print(date)
    # if date and int(date):
    #     print("Erreur type: "+str(date))
    # if titre and int(titre):
    #     print("Erreur type titre: "+str(titre))
    # if auteur and int(auteur):
    #     print("Erreur type auteur: "+str(auteur))
    return auteur+titre+str(date)

def idLivre(auteur, titre, date, curseur, nbre_lignes):
    t1=time.clock()
    curseur.execute('''SELECT rowid FROM livres WHERE idLivre = (?)''', (idRef(auteur, titre, date, curseur, nbre_lignes),))
    L = curseur.fetchone()
    # if divmod(nbre_lignes, parametres.pasTracage)[1]==0:
    #         t2 = time.clock()
    #         print(" temps de repérage de l'identifiant d'un livre "+str(t2-t1)+"secondes")
    return L[0]

def ajoutReutilisation(idSource, coordonneeSource, empanSource, texteSource, metaDataSource, idCible, coordonneeCible, empanCible, texteCible, metaDataCible, curseur, nbre_lignes):
    t1 = time.clock()
    curseur.execute('''INSERT INTO grapheReutilisations values (?,?,?, ?, ?, ?, ?, ?,?,?)''', (idSource, coordonneeSource, empanSource, texteSource, metaDataSource, idCible, coordonneeCible, empanCible, texteCible, metaDataCible))
    # if divmod(nbre_lignes, parametres.pasTracage)[1]==0:
    #         t2 = time.clock()
    #         print(" temps d'insertion d'un enregistrement "+str(t2-t1)+"secondes")

def maxNoeuds():
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    curseur.execute('''SELECT * FROM maxNoeud''')
    noeudMax = curseur.fetchone()
    return noeudMax[0]

def detruireBD():
    if 'galaxie.db' in os.listdir(parametres.DirBD):
        os.remove(parametres.DirBD+'/galaxie.db')
    if 'listeGalaxies.db' in os.listdir(parametres.DirBD):
        os.remove(parametres.DirBD+'/listeGalaxies.db')
    if 'liste_ajacence_graphe.db' in os.listdir(parametres.DirBD):
        os.remove(parametres.DirBD + '/liste_ajacence_graphe.db')
    if 'liste_ajacence_graphe_transpose.db' in os.listdir(parametres.DirBD):
        os.remove(parametres.DirBD + '/liste_ajacence_graphe_transpose.db')
    detruireListeGalaxiesBD()

def detruireListeGalaxiesBD():
    if 'galaxie.db' in os.listdir(parametres.DirBD):
        connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
        curseur = connexion.cursor()
        curseur.execute('''DROP TABLE nombreGalaxies''')
        curseur.execute('''DROP TABLE degreGalaxies''')
        curseur.execute('''CREATE TABLE nombreGalaxies (nbre INTEGER)''')
        curseur.execute('''CREATE TABLE degreGalaxies (idGalaxie INTEGER UNIQUE, degreGalaxie INTEGER)''')

        connexion.close()
    if 'listeGalaxies.db' in os.listdir(parametres.DirBD):
        os.remove(parametres.DirBD+'/listeGalaxies.db')

def reutilisations(noeud):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (noeud,))
    source = curseur.fetchall()
    curseur = connexion.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (noeud,))
    cible = curseur.fetchall()
    connexion.close()
    result = []
    for X in source+cible:
        result.append(X[0])
    return result

def valeursMetaDataSource():
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.execute('''SELECT metaDataSource FROM grapheReutilisations''')
    E =  set()
    X = curseur.fetchone()
    while X:
        E.add(X)
        X = curseur.fetchone()
    print(E)
    connexion.close()

def valeursMetaDataCible():
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.execute('''SELECT metaDataCible FROM grapheReutilisations''')
    E =  set()
    X = curseur.fetchone()
    while X:
        E.add(X)
        X = curseur.fetchone()
    print(E)
    connexion.close()

def nombreGalaxies():
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur=connexion.execute('''SELECT nbre FROM  nombreGalaxies''')
    res=curseur.fetchone()[0]
    connexion.close()
    return res


def getListeGraphe():

    graphes = os.listdir(parametres.DirGlobal + 'jsons')
    res = []
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    for i in graphes:
        tab = [int(s) for s in re.findall(r'\d+', i)]
        if len(tab) == 1:
            texte = "Galaxie numéro " + str(tab[0]) + " contenant " + str(len(dirGalaxies[str(tab[0])])) + " noeuds"
        elif len(tab) == 2:
            dirAmas = shelve.open(parametres.DirBD + '/listeAmasGalaxie' + str(tab[0]))
            texte = "Amas numéro " + str(tab[1]) + " de la galaxie " + str(tab[0]) + " contenant " + str(
                len(dirAmas[str(tab[1])])) + " noeuds"
            dirAmas.close()
        else:
            texte = 'erreur : ' + i
        res.append(texte)

    dirGalaxies.close()
    return res
