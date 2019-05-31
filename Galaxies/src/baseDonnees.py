#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import sqlite3


def create_bd(project_path):
    """

    :param project_path: The path of the current project
    :type project_path: A String
    :return:
    """
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
        ordonnee INTEGER, empan INTEGER, idGalaxie TEXT)''')
    cursor.execute('''CREATE TABLE maxNoeud (idNoeud INTEGER)''')
    cursor.execute('''CREATE TABLE nombreGalaxies (nbre INTEGER)''')
    cursor.execute('''CREATE TABLE degreGalaxies (idGalaxie TEXT UNIQUE, degreGalaxie INTEGER, 
        longueurTexteTotale INTEGER, longueurTexteMoyenne INTEGER, longueurTexteMax INTEGER)''')
    cursor.execute('''CREATE TABLE Query (idGalaxie TEXT, mark BOOLEAN)''')
    cursor.execute('''CREATE TABLE Filter (idNoeud INTEGER UNIQUE, idGalaxie TEXT, isKeep BOOLEAN, mark BOOLEAN)''')
    cursor.execute('''CREATE TABLE ListeNoeuds (idNoeud INTEGER, texte TEXT, idRowLivre INTEGER, 
        ordonnee INTEGER, empan INTEGER)''')

    cursor.execute('''CREATE INDEX idLivreSource ON grapheGalaxiesSource (idNoeud)''')
    cursor.execute('''CREATE INDEX idLivreCible ON grapheGalaxiesCible (idNoeud)''')
    cursor.execute('''CREATE INDEX refSource ON grapheReutilisations (idRefSource)''')
    cursor.execute('''CREATE INDEX refCible ON grapheReutilisations (idRefCible)''')
    cursor.execute('''CREATE INDEX idNoeud ON grapheGalaxies (idNoeudPere)''')
    cursor.execute('''CREATE INDEX idNoeudf ON grapheGalaxies (idNoeudFils)''')
    cursor.execute('''CREATE INDEX identifiantNoeud ON texteNoeuds (idNoeud)''')
    cursor.execute('''CREATE INDEX identifiantNomNoeud ON ListeNoeuds (idNoeud)''')

    connexion.commit()
    connexion.close()


def reload_query_table(cursor=None, project_path=None):
    """
        Function that erase the Query table for create a new empty one.
    This fonction is call after a new query had been made by the user

    :param cursor: cursor on the DB
    :param project_path: The path of the current project
    :type project_path: A String
    """
    is_open = False
    if cursor is None:
        connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
        cursor = connexion.cursor()
        is_open = True

    cursor.execute('''DROP TABLE Query''')
    cursor.execute('''CREATE TABLE Query (idGalaxie TEXT, mark BOOLEAN)''')

    if is_open is True:
        connexion.commit()
        connexion.close()


def reload_filter_table(cursor=None, project_path=None):
    """
        Function that erase the Filter table for create a new empty one.
    This fonction is call after a new filter query had been made by the user

    :param cursor: cursor on the DB
    :param project_path: The path of the current project
    :type project_path: A String
    """
    is_open = False
    if cursor is None:
        connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
        cursor = connexion.cursor()
        is_open = True

    cursor.execute('''DROP TABLE Filter''')
    cursor.execute('''CREATE TABLE Filter (idNoeud INTEGER UNIQUE, idGalaxie TEXT, isKeep BOOLEAN, mark BOOLEAN)''')

    if is_open is True:
        connexion.commit()
        connexion.close()


def get_filter_exist(project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    cursor.execute('''SELECT 1 FROM Filter LIMIT 1''')
    if cursor.fetchone():  # If we do have a Filter in our database
        connexion.close()
        return True
    else:
        connexion.close()
        return False


def get_filter_exist_cursor(cursor):
    cursor.execute('''SELECT 1 FROM Filter LIMIT 1''')
    return True if cursor.fetchone() else False


def dateToInt(date):
    if type(date) == type(0):
        return normalisation_date(date)
    d = date.encode('ascii', 'ignore')
    tmp = ''
    for x in filter(str.isdigit, str(d)):
        tmp = tmp + x
    if not tmp:
        return 0
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
    id = idRef(auteur, titre, date)
    curseur.execute('''SELECT * FROM livres WHERE idLivre = ?''', (id,))
    L = curseur.fetchone()
    if not L:
        date = dateToInt(date)
        curseur.execute('''INSERT INTO livres values (?,?,?,?)''', (id, auteur, titre, date))


def idRef(auteur, titre, date):
    return auteur + titre + str(date)


def idLivre(auteur, titre, date, curseur, nbre_lignes):
    curseur.execute('''SELECT rowid FROM livres WHERE idLivre = (?)''',
                    (idRef(auteur, titre, date),))
    first_line = curseur.fetchone()
    return first_line[0]


def ajoutReutilisation(idSource, coordonneeSource, empanSource, texteSource, metaDataSource, idCible, coordonneeCible,
                       empanCible, texteCible, metaDataCible, curseur):
    curseur.execute('''INSERT INTO grapheReutilisations values (?,?,?, ?, ?, ?, ?, ?,?,?)''', (
        idSource, coordonneeSource, empanSource, texteSource, metaDataSource, idCible, coordonneeCible, empanCible,
        texteCible, metaDataCible))


def maxNoeuds(data_base_path):
    connexion = sqlite3.connect(data_base_path + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    curseur.execute('''SELECT * FROM maxNoeud''')
    noeudMax = curseur.fetchone()
    return noeudMax[0]


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
