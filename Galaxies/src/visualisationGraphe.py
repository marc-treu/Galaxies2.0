#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import networkx as nx
import sqlite3
import baseDonnees


def sauveGrapheGalaxie_(numero, project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    if baseDonnees.get_filter_exist_cursor(cursor):
        cursor.execute("""SELECT idNoeud FROM Filter WHERE idGalaxie = (?) AND isKeep""", (numero,))
        list_nodes = [node[0] for node in cursor.fetchall()]
    else:
        cursor.execute("""SELECT idNoeud FROM texteNoeuds WHERE idGalaxie = (?)""", (numero,))
        list_nodes = [node[0] for node in cursor.fetchall()]

    connexion.close()
    return creerGrapheTextes_(list_nodes, 'graphe_galaxie_TC_' + str(numero), project_path)


def creerGrapheTextes_(ListeNoeuds, fichier, project_path):

    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    arcs = {}
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (Noeud,))
        L = curseur.fetchall()
        if L != []:
            arcs[Noeud] = set()
        for R in L:
            arcs[Noeud].add(R[0])
    Graphe = nx.Graph()
    for Pere in arcs.keys():
        if not Pere in Graphe:
            curseur.execute('''SELECT texte, idRowLivre FROM texteNoeuds WHERE idNoeud = (?)''', (str(Pere),))
            RefPere = curseur.fetchall()[0]
            T = caracterisquesReference(RefPere[1], curseur)

            Graphe.add_node(str(Pere), texte=RefPere[0], longueurTexte=len(RefPere[0]), auteur=T[0], titre=T[1],
                            date=T[2], reutilisation=str(baseDonnees.reutilisations(Pere, project_path)))
        l_arcs = set()
        for Fils in arcs[Pere]:
            if not Fils in Graphe:
                curseur.execute('''SELECT texte, idRowLivre FROM texteNoeuds WHERE idNoeud = (?)''', (str(Fils),))
                Ref = curseur.fetchall()[0]
                T = caracterisquesReference(str(Ref[1]), curseur)
                Graphe.add_node(str(Fils), texte=Ref[0], longueurTexte=len(Ref[0]), auteur=T[0], titre=T[1], date=T[2],
                                reutilisation=str(baseDonnees.reutilisations(Fils, project_path)))
            l_arcs.add((str(Pere), str(Fils)))

        Graphe.add_edges_from(l_arcs)

    nx.write_gexf(Graphe, project_path + '/graphs/' + fichier + '.gexf', encoding='utf-8', prettyprint=True
                  , version='1.2draft')
    connexion.close()
    return project_path + '/graphs/' + fichier + '.gexf'


def creerAmasTextes(ListeNoeuds, fichier, ext, project_path):
    # print('Création du graphe...')
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    Graphe = nx.Graph()
    arcs = {}
    for Noeud in ListeNoeuds:
        # print(Noeud)
        if Noeud != []:
            curseur.execute('''SELECT texte, idRowLivre FROM texteNoeuds WHERE idNoeud = (?)''', (Noeud,))
            L = curseur.fetchall()[0]
            # print(L)
            T = caracterisquesReference(L[1], curseur)
            # print(T)
            Graphe.add_node(Noeud, texte=L[0], longueurTexte=len(L[0]), auteur=T[0], titre=T[1], date=T[2],
                            reutilisation=str(baseDonnees.reutilisations(int(Noeud), project_path)))
            curseur.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (Noeud,))
            S = curseur.fetchall()
            # print("Noeud: "+str(Noeud)+" - arcs incidents: "+str(L))
            if S != []:
                arcs[Noeud] = set()
            for R in S:
                arcs[Noeud].add(R[0])
    l_arcs = []
    for Pere in arcs.keys():
        for Fils in arcs[Pere]:
            # print(Fils, Pere)
            if (str(Fils) in ListeNoeuds) and (Pere in ListeNoeuds):
                # print(Pere, str(Fils))
                l_arcs.append((Pere, str(Fils)))
        # print(l_arcs)
        Graphe.add_edges_from(l_arcs)
    # print(Graphe.edges())
    if (ext == 'gexf'):
        nx.write_gexf(Graphe, project_path + '/amas/' + fichier + '.' + ext, encoding='utf-8', prettyprint=True,
                      version='1.2draft')
    elif (ext == 'gml'):
        nx.write_gml(Graphe, project_path + '/amas/' + fichier + '.' + ext)
    connexion.close()


def caracterisquesReference(idRef, curseur):
    curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''',
                    (idRef,))
    return curseur.fetchall()[0]


