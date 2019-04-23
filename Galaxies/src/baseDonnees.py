#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import sqlite3
import shelve
import re
import os
import time


def create_bd(project_path):
    print("Création de la base de données 'galaxie.db'")
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    cursor.execute('''CREATE TABLE livres (idLivre TEXT UNIQUE, auteur TEXT, titre TEXT, date INTEGER)''')
    cursor.execute('''CREATE TABLE grapheReutilisations (idRefSource TEXT, ordonneeSource INTEGER, empanSource INTEGER, 
        texteSource TEXT, metaDataSource TEXT, idRefCible TEXT, ordonneeCible INTEGER, empanCible INTEGER, 
        texteCible TEXT, metaDataCible TEXT)''')
    cursor.execute('''CREATE TABLE grapheGalaxiesSource (idReutilisation INTEGER UNIQUE, idNoeud INTEGER)''')
    cursor.execute('''CREATE TABLE grapheGalaxiesCible (idReutilisation INTEGER UNIQUE, idNoeud INTEGER)''')
    cursor.execute('''CREATE TABLE grapheGalaxies (idNoeudPere INTEGER, idNoeudFils INTEGER)''')
    cursor.execute('''CREATE TABLE texteNoeuds (idNoeud INTEGER UNIQUE, texte TEXT, idRowLivre INTEGER, 
        ordonnee INTEGER, empan INTEGER)''')
    cursor.execute('''CREATE TABLE maxNoeud (idNoeud INTEGER)''')
    cursor.execute('''CREATE TABLE nombreGalaxies (nbre INTEGER)''')
    cursor.execute('''CREATE TABLE degreGalaxies (idGalaxie TEXT UNIQUE, degreGalaxie INTEGER, 
        longueurTexteTotale INTEGER, longueurTexteMoyenne INTEGER, longueurTexteMax INTEGER)''')
    cursor.execute('''CREATE TABLE Query (idGalaxie TEXT)''')

    cursor.execute('''CREATE INDEX idLivreSource ON grapheGalaxiesSource (idNoeud)''')
    cursor.execute('''CREATE INDEX idLivreCible ON grapheGalaxiesCible (idNoeud)''')
    cursor.execute('''CREATE INDEX refSource ON grapheReutilisations (idRefSource)''')
    cursor.execute('''CREATE INDEX refCible ON grapheReutilisations (idRefCible)''')
    cursor.execute('''CREATE INDEX idNoeud ON grapheGalaxies (idNoeudPere)''')
    cursor.execute('''CREATE INDEX idNoeudf ON grapheGalaxies (idNoeudFils)''')
    cursor.execute('''CREATE INDEX identifiantNoeud ON texteNoeuds (idNoeud)''')
    # cursor.execute('''CREATE INDEX dateIndex ON livres (date) ASC''')
    # cursor.execute('''CREATE INDEX idReutSource ON grapheGalaxiesSource (idReutilisation)''')
    # cursor.execute('''CREATE INDEX idReutCible ON grapheGalaxiesCible (idReutilisation)''')
    #
    # cursor.execute('''CREATE INDEX refLivre ON livres (idLivre)''')
    connexion.commit()
    connexion.close()


def reload_query_table(cursor):
    """
        Function that erase the Query table for create a new empty one.
    This fonction is call after a new query had been made by the user

    :param cursor: cursor on the DB
    """
    cursor.execute('''DROP TABLE Query''')
    cursor.execute('''CREATE TABLE Query (idGalaxie TEXT)''')


def dateToInt(date):
    # print(date)
    # if not date or date=='' or date=='....':
    #     return ''
    if type(date) == type(0):
        return normalisation_date(date)
    d = date.encode('ascii', 'ignore')
    # print(d)
    tmp = ''
    for x in filter(str.isdigit, str(d)):
        tmp = tmp + x
    # print(type(tmp))
    if not tmp:
        return 0  # correction '' remplacé par 0
    if len(tmp) > 4:
        tmp = tmp[:4]
    date = int(tmp)
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
        date = dateToInt(date)
        curseur.execute('''INSERT INTO livres values (?,?,?,?)''', (id, auteur, titre, date))


def idRef(auteur, titre, date, curseur, nbre_lignes):
    # print(date)
    # if date and int(date):
    #     print("Erreur type: "+str(date))
    # if titre and int(titre):
    #     print("Erreur type titre: "+str(titre))
    # if auteur and int(auteur):
    #     print("Erreur type auteur: "+str(auteur))
    return auteur + titre + str(date)


def idLivre(auteur, titre, date, curseur, nbre_lignes):
    curseur.execute('''SELECT rowid FROM livres WHERE idLivre = (?)''',
                    (idRef(auteur, titre, date, curseur, nbre_lignes),))
    first_line = curseur.fetchone()
    return first_line[0]


def ajoutReutilisation(idSource, coordonneeSource, empanSource, texteSource, metaDataSource, idCible, coordonneeCible,
                       empanCible, texteCible, metaDataCible, curseur, nbre_lignes):
    curseur.execute('''INSERT INTO grapheReutilisations values (?,?,?, ?, ?, ?, ?, ?,?,?)''', (
    idSource, coordonneeSource, empanSource, texteSource, metaDataSource, idCible, coordonneeCible, empanCible,
    texteCible, metaDataCible))


def maxNoeuds(data_base_path):
    connexion = sqlite3.connect(data_base_path + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    curseur.execute('''SELECT * FROM maxNoeud''')
    noeudMax = curseur.fetchone()
    return noeudMax[0]


def detruireBD(project_path):
    if 'galaxie.db' in os.listdir(project_path + '/BDs'):
        os.remove(project_path + '/BDs/galaxie.db')
    if 'listeGalaxies.db' in os.listdir(project_path + '/BDs'):
        os.remove(project_path + '/BDs/listeGalaxies.db')
    if 'liste_ajacence_graphe.db' in os.listdir(project_path + '/BDs'):
        os.remove(project_path + '/BDs/liste_ajacence_graphe.db')
    if 'liste_ajacence_graphe_transpose.db' in os.listdir(project_path + '/BDs'):
        os.remove(project_path + '/BDs/liste_ajacence_graphe_transpose.db')
    detruireListeGalaxiesBD()


def detruireListeGalaxiesBD(project_path):
    if 'galaxie.db' in os.listdir(project_path + '/BDs'):
        connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
        curseur = connexion.cursor()
        curseur.execute('''DROP TABLE nombreGalaxies''')
        curseur.execute('''DROP TABLE degreGalaxies''')
        curseur.execute('''CREATE TABLE nombreGalaxies (nbre INTEGER)''')
        curseur.execute('''CREATE TABLE degreGalaxies (idGalaxie INTEGER UNIQUE, degreGalaxie INTEGER)''')

        connexion.close()
    if 'listeGalaxies.db' in os.listdir(project_path + '/BDs'):
        os.remove(project_path + '/BDs/listeGalaxies.db')


def reutilisations(noeud, project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (noeud,))
    source = curseur.fetchall()
    curseur = connexion.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (noeud,))
    cible = curseur.fetchall()
    connexion.close()
    result = []
    for X in source + cible:
        result.append(X[0])
    return result


def valeursMetaDataSource(project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.execute('''SELECT metaDataSource FROM grapheReutilisations''')
    E = set()
    X = curseur.fetchone()
    while X:
        E.add(X)
        X = curseur.fetchone()
    print(E)
    connexion.close()


def valeursMetaDataCible(project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.execute('''SELECT metaDataCible FROM grapheReutilisations''')
    E = set()
    X = curseur.fetchone()
    while X:
        E.add(X)
        X = curseur.fetchone()
    print(E)
    connexion.close()


def nombreGalaxies(project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.execute('''SELECT nbre FROM  nombreGalaxies''')
    res = curseur.fetchone()[0]
    connexion.close()
    return res


# def get_list_graph(project_path):
#     graphs = os.listdir(project_path + "/jsons")
#     res = []
#     dirGalaxies = shelve.open(project_path + '/BDs/listeGalaxies')
#     for i in graphs:
#         tab = [int(s) for s in re.findall(r'\d+', i)]
#         if len(tab) == 1:
#             texte = "Galaxie numéro " + str(tab[0]) + " contenant " + str(len(dirGalaxies[str(tab[0])])) + " noeuds"
#         elif len(tab) == 2:
#             dirAmas = shelve.open(project_path + '/BDs/listeAmasGalaxie' + str(tab[0]))
#             texte = "Amas numéro " + str(tab[1]) + " de la galaxie " + str(tab[0]) + " contenant " + str(
#                 len(dirAmas[str(tab[1])])) + " noeuds"
#             dirAmas.close()
#         else:
#             texte = 'erreur : ' + i
#         res.append(texte)
#
#     dirGalaxies.close()
#     return res
