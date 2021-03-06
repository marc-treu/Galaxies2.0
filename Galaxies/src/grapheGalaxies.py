#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import sqlite3
import time


class noeud:  # permet d'énumérer les noeuds du graphe
    def __init__(self):
        self.val = 0
        self.tempsIni = time.clock()
        self.pasNbreNoeud = 10000

    def nouvelleValeur(self):
        self.val += 1
        if divmod(self.val, self.pasNbreNoeud)[1] == 0:
            self.temps = time.clock()
            print("Nombre noeuds du graphe: " + str(self.val) + "; temps de construction du graphe pour les " + str(
                self.pasNbreNoeud) + " derniers noeuds: " + format(self.temps - self.tempsIni, 'f') + " sec.")
            self.tempsIni = self.temps
        return self.val

    def valeur(self):
        return self.val


def construction_graphe(project_path):
    """
    Fonction qui va construire le Graphe
    """
    t1 = time.clock()
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    n = noeud()
    cursor.execute('''SELECT rowid FROM livres''')
    idReference = cursor.fetchone()  # permet de prendre le premier
    while idReference != None:  # On va parcourir toute notre TABLE livres
        fusion_sources_cibles(idReference, connexion, n)
        idReference = cursor.fetchone()
    cursor.execute('''INSERT INTO maxNoeud values (?)''', (n.val,))
    connexion.commit()
    connexion.close()
    t2 = time.clock()
    print("Temps de construction du graphe: " + format(t2 - t1, 'f') + " sec.")
    return n.val


def fusion_sources_cibles(idRef, c, n):
    """

    idRef : l'id d'une des lignes du tableau qui est de la forme (n,)
    c : un pipe qui est connecté a notre BD
    n : la class Noeud qui permet de compter les noeuds de notre graphe
    """

    curseurSource = c.cursor()  # On creer deux curseur
    curseurCible = c.cursor()
    curseurSource.execute('''SELECT ordonneeSource, empanSource, rowid FROM grapheReutilisations WHERE idRefSource = 
                        ?''', idRef)
    curseurCible.execute('''SELECT ordonneeCible, empanCible, rowid FROM grapheReutilisations WHERE idRefCible = ?''',
                         idRef)

    listeReutilisationSource = curseurSource.fetchall()
    listeReutilisationCible = curseurCible.fetchall()
    listeReutilisationMarquee = marquage(listeReutilisationCible, 'cible') + listeReutilisationSource
    listeReutilisationMarquee.sort()
    R = fusion(listeReutilisationMarquee, n)

    if R:
        n.nouvelleValeur()
    for X in R:
        if X[-2] > 0:
            ajoutSource(X, curseurSource)
        elif X[-2] < 0:
            ajoutCible(X, curseurCible)
        else:
            print("Attention, erreur fusion sur noeud " + str(n.val) + " avec X=" + str(X))


def marquage(L, M):
    R = []
    for X in L:
        if M == 'cible':
            R.append((X[0], X[1], -X[2]))
        else:
            R.append(X)
    return R


def fusion(L, n):
    if L is []:
        return []
    elif len(L) == 1:
        return [[L[0][0], L[0][1], L[0][2], n.val]]
    else:
        Tete = L[0]
        Suivant = L[1]
        return fusion_aux(Tete, Suivant, L[2:], n, [])


def fusion_aux(Tete, Suivant, Entree, Noeud, Resultat):
    R = Resultat
    E = Entree
    T = Tete
    S = Suivant
    while len(E) >= 1:
        if T[0] + T[1] >= S[0]:
            NReutilisation = [T[0], max(T[1], S[1] - T[0] + S[0]), T[2], Noeud.val]
            R = R + [NReutilisation]
            T = [T[0], max(T[1], S[1] - T[0] + S[0]), S[2]]
            S = E[0]
            E = E[1:]
        else:
            NReutilisation = [T[0], T[1], T[2], Noeud.val]
            R = R + [NReutilisation]
            T = S
            S = E[0]
            E = E[1:]
            Noeud.nouvelleValeur()
    else:
        if T[0] + T[1] >= S[0]:
            NReutilisation = [T[0], max(T[1], S[1] - T[0] + S[0]), T[2], Noeud.val]
            R = R + [NReutilisation]
            T = [T[0], max(T[1], S[1] - T[0] + S[0]), S[2]]
        else:
            NReutilisation = [T[0], T[1], T[2], Noeud.val]
            R = R + [NReutilisation]
            T = S
            Noeud.nouvelleValeur()

    return R + [[T[0], T[1], T[2], Noeud.val]]


def ajoutSource(L, Curseur):
    Curseur.execute('''INSERT INTO grapheGalaxiesSource values (?,?)''', (L[2], L[3],))


def ajoutCible(L, Curseur):
    Curseur.execute('''INSERT INTO grapheGalaxiesCible values (?,?)''', (abs(L[2]), L[3],))


def sauvegarde_graphe(project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur_arc = connexion.cursor()
    curseur_noeud = connexion.cursor()
    curseur_graphe = connexion.cursor()
    curseur_arc.execute('''SELECT * FROM maxNoeud''')
    maxNoeud = curseur_arc.fetchone()[0]
    n = noeud()
    while n.val < maxNoeud:
        curseur_arc.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (n.val,))
        reutilisation = curseur_arc.fetchone()
        while reutilisation != None:
            curseur_noeud.execute('''SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = (?)''',
                                  (reutilisation[0],))
            nouveau_noeud = curseur_noeud.fetchone()
            curseur_graphe.execute('''INSERT INTO grapheGalaxies values (?,?)''', (n.val, nouveau_noeud[0],))
            reutilisation = curseur_arc.fetchone()
        n.nouvelleValeur()
    print("graphe sauvé")
    n = noeud()
    while n.val < maxNoeud:
        curseur_arc.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (n.val,))
        reutilisation = curseur_arc.fetchone()
        while reutilisation != None:
            curseur_noeud.execute('''SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = (?)''',
                                  (reutilisation[0],))
            nouveau_noeud = curseur_noeud.fetchone()
            curseur_graphe.execute('''INSERT INTO grapheGalaxies values (?,?)''', (n.val, nouveau_noeud[0],))
            reutilisation = curseur_arc.fetchone()
        n.nouvelleValeur()
    connexion.commit()
    connexion.close()
    print("graphe transposé sauvé")
