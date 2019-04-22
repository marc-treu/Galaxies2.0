#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import networkx as nx
import shelve
import parametres
import sqlite3
import baseDonnees
import filtres
import codecs
import json


def sauveGrapheGalaxie(numero, project_path):
    dirGalaxies = shelve.open(project_path + '/BDs/listeGalaxies')
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    return creerGrapheTextes(ListeNoeuds, 'graphe_galaxie_TC_' + str(numero), 'gexf', project_path)


def sauveGrapheGalaxieGML(numero):
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    ListeNoeuds = dirGalaxies[str(numero)]
    # print("Liste des nœuds: "+str(ListeNoeuds))
    dirGalaxies.close()
    return creerGrapheTextes(ListeNoeuds, 'graphe_galaxie_TC_' + str(numero), 'gml')


def sauveGrapheGalaxieAffichage(requete, numero):
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    ListeNoeuds = dirGalaxies[str(numero)]
    # print("Liste des nœuds: "+str(ListeNoeuds))
    dirGalaxies.close()
    creerGrapheTextesFiltre(requete, ListeNoeuds, 'graphe_galaxie_TC_' + str(numero) + '.gexf')


# def sauveGrapheGalaxieFiltreListe(Lrequete, numero):
#     dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
#     ListeNoeuds = dirGalaxies[str(numero)]
#     #print("Liste des nœuds: "+str(ListeNoeuds))
#     dirGalaxies.close()
#     creerGrapheTextesFiltreListe(Lrequete, ListeNoeuds, 'graphe_galaxie_TC_'+str(numero)+'.gexf')

def sauveGrapheAmas_(numGalaxie, dictAmas, project_path):
    dirAmas = shelve.open(project_path + '/BDs/listeAmasGalaxie' + str(numGalaxie))
    for i in dictAmas:
        creerAmasTextes(dirAmas[str(i)], 'graphe_galaxie_' + str(numGalaxie) + '_amas_' + str(i), 'gexf', project_path)
    dirAmas.close()


# def sauveGrapheAmas(listeNoeuds, galaxie_numero, amas_numero):
#     creerGrapheTextes(listeNoeuds, 'graphe_galaxie_'+galaxie_numero+'_amas_'+amas_numero, 'gexf')

# def sauveGrapheAmasAffichage(requete, listeNoeuds, galaxie_numero, amas_numero):
#     creerGrapheTextesFiltre(requete, listeNoeuds, 'graphe_galaxie_' + galaxie_numero + '_amas_' + amas_numero + '.gexf')


def creerGrapheTextes(ListeNoeuds, fichier, ext, project_path):
    # print('Création du graphe...')
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    # reutilisations = set()
    arcs = {}
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (Noeud,))
        L = curseur.fetchall()
        # print("Noeud: "+str(Noeud)+" - arcs incidents: "+str(L))
        if L != []:
            arcs[Noeud] = set()
        for R in L:
            arcs[Noeud].add(R[0])

    Graphe = nx.Graph()
    #    idRef = set()
    #    print("Ensemble des réutilisations: "+ str(reutilisations))
    # print('Arcs émergents: '+str(arcs_emergents)+" - arcs incidents: "+str(arcs_incidents))
    for Pere in arcs.keys():
        # print("Arcs émergents noeud "+str(X)+": "+str(arcs_emergents[X]))
        # if(Pere%10000==0):
        #     print(Pere)
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
    if (ext == 'json'):
        data = nx.readwrite.json_graph.node_link_data(Graphe)
        with open(project_path + '/graphs/' + fichier + '.' + ext, 'w') as f:
            json.dump(data, f)
    if (ext == 'gexf'):
        nx.write_gexf(Graphe, project_path + '/graphs/' + fichier + '.' + ext, encoding='utf-8', prettyprint=True,
                      version='1.2draft')
    if (ext == 'gml'):
        nx.write_gml(Graphe, project_path + '/graphs/' + fichier + '.' + ext)
        # print(str(nx.generate_gml(Graphe)))
    # sauvJson(Graphe, parametres.DirBD + '/' + fichier)
    connexion.close()
    return project_path + '/graphs/' + fichier + '.' + ext


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


def creerGrapheTextesFiltre(requete, ListeNoeuds, fichier):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    # reutilisations = set()
    arcs = {}
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (Noeud,))
        L = curseur.fetchall()
        # print("Noeud: "+str(Noeud)+" - arcs incidents: "+str(L))
        if L != []:
            arcs[Noeud] = set()
        for R in L:
            arcs[Noeud].add(R[0])

    Graphe = nx.Graph()
    #    idRef = set()
    #    print("Ensemble des réutilisations: "+ str(reutilisations))
    # print('Arcs émergents: '+str(arcs_emergents)+" - arcs incidents: "+str(arcs_incidents))
    for Pere in arcs.keys():
        # print("Arcs émergents noeud "+str(X)+": "+str(arcs_emergents[X]))
        LNoeudsActifs = []
        if not Pere in Graphe:
            curseur.execute('''SELECT texte, idRowLivre FROM texteNoeuds WHERE idNoeud = (?)''', (str(Pere),))
            RefPere = curseur.fetchall()[0]
            T = caracterisquesReference(RefPere[1], curseur)
            LPere = [str(Pere), RefPere[0], len(RefPere[0]), T[0], T[1], T[2], str(baseDonnees.reutilisations(Pere))]
            if filtres.filtreAffichage(requete, len(RefPere[0]), T[0], T[1], T[2]):
                RequetePere = True
            else:
                RequetePere = False
            l_arcs = set()
            LFils = []
            for Fils in arcs[Pere]:
                if not Fils in Graphe:
                    curseur.execute('''SELECT texte, idRowLivre FROM texteNoeuds WHERE idNoeud = (?)''', (str(Fils),))
                    Ref = curseur.fetchall()[0]
                    T = caracterisquesReference(str(Ref[1]), curseur)
                    if RequetePere == True or filtres.filtreAffichage(requete, len(Ref[0]), T[0], T[1], T[2]):
                        LFils.append(
                            [str(Fils), Ref[0], len(Ref[0]), T[0], T[1], T[2], str(baseDonnees.reutilisations(Fils))])
            if LFils:
                Graphe.add_node(LPere[0], texte=LPere[1], longueurTexte=LPere[2], auteur=LPere[3], titre=LPere[4],
                                date=LPere[5], reutilisation=LPere[6])
                for Noeud in LFils:
                    Graphe.add_node(Noeud[0], texte=Noeud[1], longueurTexte=Noeud[2], auteur=Noeud[3], titre=Noeud[4],
                                    date=Noeud[5], reutilisation=Noeud[6])
                    l_arcs.add((str(Pere), Noeud[0]))

            Graphe.add_edges_from(l_arcs)

    nx.write_gexf(Graphe, parametres.DirGraphes + '/' + fichier, encoding='utf-8', prettyprint=True, version='1.2draft')
    # nx.write_gml(Graphe, parametres.DirGraphes+'/'+fichier)
    # sauvJson(Graphe, parametres.DirGraphes+'/' + fichier)
    connexion.close()


def ajoutNoeudFiltre(Graphe, noeud, texte, longueur, auteur, titre, date, reutilisation):
    Graphe.add_node(noeud, texte=texte, longueurTexte=longueur, auteur=auteur, titre=titre, date=date,
                    reutilisation=reutilisation)


def caracterisquesReference(idRef, curseur):
    curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''',
                    (idRef,))
    return curseur.fetchall()[0]


def ajustementTexte(texte):
    return texte
    # Ltexte = textwrap.wrap(texte, parametres.largeurAjustement)
    # Stexte=""
    # for X in Ltexte:
    #     Stexte=Stexte+"\\n"+X
    # return Stexte+"\\n"


def sauvJson(Graphe, fichier):
    fic = fichier[:-4] + "tab"
    L = nx.jit_data(Graphe)
    sortie = codecs.open(fic, 'w')
    sortie.write(L)
    sortie.close()
