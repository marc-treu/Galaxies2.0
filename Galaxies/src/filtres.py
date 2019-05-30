#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import parametres

FILTRE = ['empan', 'auteur', '-auteur', 'mots_titre', '-mots_titre', 'date']


def filtreLivres(requete, LLivre):
    """

    :param requete:
    :param LLivre: auteur, titre, date, empan, texte FROM texteNoeuds
    :return:
    """

    clefs = requete.keys()

    if not any(clef in FILTRE for clef in clefs):  # If we don't have any of those FILTRE keys in the query
        return True  # We return True

    if 'empan' in clefs:
        if not LLivre[3] > requete['empan']:
            return False
    if 'auteur' in clefs:
        if not any(name.lower() in LLivre[0].lower() for name in requete['auteur']):
            return False
    if 'mots_titre' in clefs:
        if not any(word.lower() in LLivre[1].lower() for word in requete['mots_titre']):
            return False
    if '-auteur' in clefs:
        if any(name.lower() in LLivre[0].lower() for name in requete['-auteur']):
            return False
    if '-mots_titre' in clefs:
        if any(word.lower() in LLivre[1].lower() for word in requete['-mots_titre']):
            return False
    if 'date' in clefs:
        if not testNum(LLivre[2], requete['date']):
            return False
    if 'text' in clefs:
        if not any(word.lower() in LLivre[4].lower() for word in requete['text']):
            return False
    if '-text' in clefs:
        if any(word.lower() in LLivre[4].lower() for word in requete['-text']):
            return False
    return True


def filtreMetaData(requete, MetaData):
    # print("Metadate: "+str(MetaData)+" Clefs"+str(requete.keys()))
    clefs = requete.keys()
    if parametres.metaDataSource in clefs:
        # print("Clefs " + str(parametres.metaDataSource))
        if parametres.metaDataSourceType == 'TEXT':
            if not str.lower(requete[parametres.metaDataSource]) in str.lower(MetaData[0]):
                return False
        elif parametres.metaDataSourceType == 'NUM' and type(requete[parametres.metaDataSource]) == type(1):
            if not testNum(MetaData[0], requete[parametres.metaDataSource]):
                return False
    if parametres.metaDataCible in clefs:
        if parametres.metaDataCibleType == 'TEXT':
            if not str.lower(requete[parametres.metaDataCible]) in str.lower(MetaData[1]):
                return False
        elif parametres.metaDataCibleType == 'NUM' and type(requete[parametres.metaDataCible]) == type([]):

            if type(MetaData[1]) == type(1):
                MD = MetaData[1]
            elif chaineChiffres(MetaData[1]):
                MD = int(MetaData[1])
            elif len(MetaData[1]) > 1 and MetaData[1][0] == '1' and MetaData[1][1] == '8':
                MD = 1800
            else:
                return True
            # print("Méta donnée", parametres.metaDataCible, " valeur: ", MD)
            if not testNum(MD, requete[parametres.metaDataCible]):
                return False
    return True


def filtreAffichage(requete, longueur, auteur, titre, date):
    LClefs = requete.keys()
    if 'auteur' in LClefs:
        for X in requete["auteur"]:
            if not str.lower(X) in str.lower(auteur):
                return False
    if '-auteur' in LClefs:
        for X in requete["-auteur"]:
            if str.lower(X) in str.lower(auteur):
                return False
    if 'date' in LClefs:
        if not testNum(date, requete['date']):
            return False
    if 'mots_titre' in LClefs:
        for X in requete['mots_titre']:
            if not str.lower(X) in str.lower(titre):
                return False
    if '-mots_titre' in LClefs:
        for X in requete['-mots_titre']:
            if str.lower(X) in str.lower(titre):
                return False
    if 'empan' in LClefs:
        if requete['empan'] > longueur:
            return False
    return True


def chaineChiffres(S):
    if S == '':
        return False
    for X in S:
        if not X in '0123456789':
            return False
    return True


def testNum(N, Couple):
    if id(type(N)) != id(type(1)):
        return True
    elif id(type(Couple)) == id(type([])) and len(Couple) == 2:
        if id(type(Couple[0])) == id(type(1)):
            if not N >= Couple[0]:
                return False
        if id(type(Couple[1])) == id(type(1)):
            if not N <= Couple[1]:
                return False
    return True


def filtreLongueurMaximale(LGalaxie, Nombre, curseur, dirGalaxies):
    LGalaxieFinale = []
    for NumGal in LGalaxie:
        EnsNoeuds = dirGalaxies[str(NumGal)]
        LongueurMin = False
        while EnsNoeuds and LongueurMin is False:
            if longueurTexteNoeud(EnsNoeuds.pop(), curseur) >= Nombre:
                LongueurMin = True
            if LongueurMin:
                LGalaxieFinale.append(NumGal)
    return LGalaxieFinale


def longueurTexteNoeud(Noeud, curseur):
    curseur.execute('''SELECT texte FROM texteNoeuds WHERE idNoeud = (?)''', (Noeud,))
    return len(curseur.fetchall()[0][0])


def choixRequeteSauvegarde(L):
    print(
        "Souhaitez-vous sauver et filtrer les résultats dans l'affichage du graphe? \n(Si oui, donnez un nombre entre 1 et ",
        len(L), " qui correspond à la requête choisie, si vous ne voulez pas de filtre, mettez 0)")
    for i in range(len(L)):
        print(i + 1, ") ", L[i])
    C = input("Requête choisie: ")
    if not chaineChiffres(C):
        return choixRequeteSauvegarde(L)
    elif int(C) == 0:
        return False
    elif int(C) > len(L):
        print("Le nombre doit être compris entre 0 et ", len(L))
        return choixRequeteSauvegarde(L)
    else:
        return L[int(C) - 1]
