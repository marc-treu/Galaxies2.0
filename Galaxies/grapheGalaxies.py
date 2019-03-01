#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import sqlite3
import parametres
import time
import shelve

class noeud: #permet d'énumérer les noeuds du graphe
    def __init__(self):
        self.val = 0
        self.tempsIni = time.clock()
    def nouvelleValeur(self):
        self.val += 1
        if divmod(self.val, parametres.pasNbreNoeud)[1] == 0:
            self.temps = time.clock()
            print("Nombre noeuds du graphe: "+str(self.val)+"; temps de construction du graphe pour les "+str(parametres.pasNbreNoeud)+" derniers noeuds: "+format(self.temps - self.tempsIni, 'f')+" sec.")
            self.tempsIni = self.temps
        return self.val
    def valeur(self):
        return self.val

def construction_graphe():
    t1 = time.clock()
    connexion = sqlite3.connect(parametres.DirBD+'/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    n = noeud()
    curseur.execute('''SELECT rowid FROM livres''')
    idReference = curseur.fetchone()
    while idReference != None:
        fusion_sources_cibles(idReference, connexion, n)
        # fusion_sources(idReference, connexion, n)
        #connexion.commit()
        # fusion_cibles(idReference, connexion, n)
        # connexion.commit()
        idReference = curseur.fetchone()
    curseur.execute('''INSERT INTO maxNoeud values (?)''', (n.val,))
    connexion.commit()
    connexion.close()
    t2 = time.clock()
    print("Temps de construction du graphe: "+format(t2 - t1,'f')+" sec.")
    return (n.val)

def fusion_sources_cibles(idRef, c, n):
    #print("appel fusion sur référence"+str(idRef))
    curseurSource=c.cursor()
    curseurCible=c.cursor()
    #print("Fusion sources idRef: "+str(idRef[0]))
    curseurSource.execute('''SELECT ordonneeSource, empanSource, rowid FROM grapheReutilisations WHERE idRefSource = ?''', idRef)
    curseurCible.execute('''SELECT ordonneeCible, empanCible, rowid FROM grapheReutilisations WHERE idRefCible = ?''', idRef)
    listeReutilisationSource = curseurSource.fetchall()
    #print("liste réutilisation source: "+str(listeReutilisationSource))
    listeReutilisationCible = curseurCible.fetchall()
    #print("liste réutilisation cible: " + str(listeReutilisationCible))
    listeReutilisationMarquee = marquage(listeReutilisationCible, 'cible')+listeReutilisationSource
    listeReutilisationMarquee.sort()
    R = fusion(listeReutilisationMarquee, idRef, n)
    # if listeReutilisationSource != [] and listeReutilisationCible != []:
    #     print("liste réutilisation source: " + str(listeReutilisationSource))
    #     print("liste réutilisation cible: " + str(listeReutilisationCible))
    #     print("Résultat fusion:"+str(R))
    if R:
        n.nouvelleValeur()
    for X in R:
        if X[-2] > 0:
            ajoutSource(X, curseurSource)
        elif X[-2] < 0:
            ajoutCible(X, curseurCible)
        else:
            print("Attention, erreur fusion sur noeud "+str(n.val)+" avec X="+str(X))
    #print(R)


def marquage(L, M):
    R = []
    for X in L:
        if M == 'cible':
            R.append((X[0], X[1], -X[2]))
        else:
            R.append(X)
    return R



def fusion(L, idRef, n):
    if L == []:
        return []
    elif len(L) == 1:
        return [[L[0][0], L[0][1], L[0][2], n.val]]
    else:
        Tete =  L[0]
        Suivant = L[1]
        return fusionAux(Tete, Suivant, L[2:], n, [])

def fusionAux(Tete, Suivant, Entree, Noeud, Resultat):
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

    return R+[[T[0],T[1],T[2], Noeud.val]]




def ajoutSource(L, Curseur):
    Curseur.execute('''INSERT INTO grapheGalaxiesSource values (?,?)''', (L[2],L[3],))


def ajoutCible(L, Curseur):
    Curseur.execute('''INSERT INTO grapheGalaxiesCible values (?,?)''', (abs(L[2]),L[3],))

def sauvegarde_graphe():
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur_arc = connexion.cursor()
    curseur_noeud = connexion.cursor()
    curseur_graphe = connexion.cursor()
    curseur_arc.execute('''SELECT * FROM maxNoeud''')
    maxNoeud = curseur_arc.fetchone()[0]
    graphe = shelve.open(parametres.DirBD+'/liste_ajacence_graphe')
    n = noeud()
    while n.val < maxNoeud:
        curseur_arc.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (n.val,))
        reutilisation = curseur_arc.fetchone()
        #print("Noeud: "+str(n.val)+"; reutilisation: "+str(reutilisation))
        liste_adjacence = []
        while reutilisation != None:
            #print("     - Noeud fils: "+str(reutilisation))
            curseur_noeud.execute('''SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = (?)''', (reutilisation[0],))
            nouveau_noeud = curseur_noeud.fetchone()
            liste_adjacence.append(nouveau_noeud[0])
            curseur_graphe.execute('''INSERT INTO grapheGalaxies values (?,?)''', (n.val, nouveau_noeud[0], ))
            reutilisation = curseur_arc.fetchone()
        #print("Ensemble des fils de "+str(n.val)+": "+str(liste_adjacence))
        graphe[str(n.val)]=liste_adjacence
        n.nouvelleValeur()
    graphe.close()
    print("graphe sauvé")
    graphe_t = shelve.open(parametres.DirBD+'/liste_ajacence_graphe_transpose')
    n = noeud()
    while n.val < maxNoeud:
        curseur_arc.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (n.val,))
        reutilisation = curseur_arc.fetchone()
        #print("Noeud: "+str(n.val)+"; reutilisation: "+str(reutilisation))
        liste_adjacence = []
        while reutilisation != None:
            #print("     - Noeud fils: "+str(reutilisation))
            curseur_noeud.execute('''SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = (?)''', (reutilisation[0],))
            nouveau_noeud = curseur_noeud.fetchone()
            liste_adjacence.append(nouveau_noeud[0])
            curseur_graphe.execute('''INSERT INTO grapheGalaxies values (?,?)''', (n.val, nouveau_noeud[0],))
            reutilisation = curseur_arc.fetchone()
        #print("Ensemble des fils de "+str(n.val)+": "+str(liste_adjacence))
        graphe_t[str(n.val)]=liste_adjacence
        n.nouvelleValeur()
    graphe_t.close()
    connexion.commit()
    connexion.close()
    print("graphe transposé sauvé")

def sauvegarde_graphe_():
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur_arc = connexion.cursor()
    curseur_noeud = connexion.cursor()
    curseur_graphe = connexion.cursor()
    curseur_arc.execute('''SELECT * FROM maxNoeud''')
    maxNoeud = curseur_arc.fetchone()[0]
    #graphe = shelve.open(parametres.DirBD+'/liste_ajacence_graphe')
    n = noeud()
    while n.val < maxNoeud:
        curseur_arc.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (n.val,))
        reutilisation = curseur_arc.fetchone()
        #print("Noeud: "+str(n.val)+"; reutilisation: "+str(reutilisation))
        #liste_adjacence = []
        while reutilisation != None:
            #print("     - Noeud fils: "+str(reutilisation))
            curseur_noeud.execute('''SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = (?)''', (reutilisation[0],))
            nouveau_noeud = curseur_noeud.fetchone()
            #liste_adjacence.append(nouveau_noeud[0])
            curseur_graphe.execute('''INSERT INTO grapheGalaxies values (?,?)''', (n.val, nouveau_noeud[0], ))
            reutilisation = curseur_arc.fetchone()
        #print("Ensemble des fils de "+str(n.val)+": "+str(liste_adjacence))
        #graphe[str(n.val)]=liste_adjacence
        n.nouvelleValeur()
    #graphe.close()
    print("graphe sauvé")
    #graphe_t = shelve.open(parametres.DirBD+'/liste_ajacence_graphe_transpose')
    n = noeud()
    while n.val < maxNoeud:
        curseur_arc.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (n.val,))
        reutilisation = curseur_arc.fetchone()
        #print("Noeud: "+str(n.val)+"; reutilisation: "+str(reutilisation))
        #liste_adjacence = []
        while reutilisation != None:
            #print("     - Noeud fils: "+str(reutilisation))
            curseur_noeud.execute('''SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = (?)''', (reutilisation[0],))
            nouveau_noeud = curseur_noeud.fetchone()
            #liste_adjacence.append(nouveau_noeud[0])
            curseur_graphe.execute('''INSERT INTO grapheGalaxies values (?,?)''', (n.val, nouveau_noeud[0],))
            reutilisation = curseur_arc.fetchone()
        #print("Ensemble des fils de "+str(n.val)+": "+str(liste_adjacence))
        #graphe_t[str(n.val)]=liste_adjacence
        n.nouvelleValeur()
    #graphe_t.close()
    connexion.commit()
    connexion.close()
    print("graphe transposé sauvé")




def grapheConstruit():
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    curseur.execute('''SELECT * FROM grapheGalaxiesSource''')
    return curseur.fetchone()




def egal(L1, L2):
    if len(L1) != len(L2):
        return None
    for x in L1:
        if not x in L2:
            return None
    return L1
