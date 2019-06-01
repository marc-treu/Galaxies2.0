#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import baseDonnees
import codecs
import json
import os
import parametres
import pickle
import shutil
import sqlite3
import time


def lecture(tab_file, project_path, number_of_line=0):
    """
    Lit le fichier tab_file passer en parametres et remplie la base de donnée

    :param tab_file:
    :param project_path:
    :param number_of_line:
    :return:
    """
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db')
    curseur = connexion.cursor()
    nbre_ligne = 0

    t1 = time.clock()
    for line in codecs.open(tab_file, 'r', 'utf-8', errors="ignore"):
        if nbre_ligne > number_of_line != 0:
            return
        nbre_ligne += 1
        L=json.loads(line.rstrip())

        baseDonnees.ajoutLivre(item('source_author', L),
                               item('source_title', L),
                               itemNum('source_create_date', L), curseur, nbre_ligne)
        baseDonnees.ajoutLivre(item('target_author', L),
                               item('target_title', L),
                               itemNum('target_create_date', L), curseur, nbre_ligne)
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
                                       curseur)
        if divmod(nbre_ligne, parametres.pasTracage)[1] == 0:  # permet de tenir au courant l'utilisateur
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


def init_directory(project_path):
    """
        initializes the creation of folders, for the current project

    :param project_path: The path of the project
    """
    os.mkdir(project_path)
    os.mkdir(project_path + '/BDs')
    os.mkdir(project_path + '/amas')
    os.mkdir(project_path + '/graphs')
    os.mkdir(project_path + '/jsons')
    shutil.copy('./code.js', project_path + '/')
    shutil.copy('./index.html', project_path + '/')


def save_query(query, filter_, project_path):
    queries = {"query": query, "filter": filter_}
    pickle.dump(queries, open(project_path + '/query', 'wb'))


def load_query(project_path):
    try:
        return pickle.load(open(project_path + '/query', 'rb'))
    except:
        return None


def parse_lemmas(file_path):

    result = dict()
    with open(file_path, "r+") as file:
        line = file.readline()
        while line:
            print("line =", line)
            line = line.split()
            result[line[0]] = line[1]
            line = file.readline()

    return result
