#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import sqlite3
import parametres
import time
import shelve
import os
import filtres
import visualisationGraphe
import cProfile
import grapheGalaxies

import baseDonnees
# import unicodedata
# from django.utils import encoding

class galaxie: #permet d'énumérer composantes connexes
    def __init__(self):
        self.val = 0
        self.compositionGalaxie = dict()
        self.tempsIni = time.clock()
    def nouvelleValeur(self):
        self.val += 1
        if divmod(self.val, parametres.pasGalaxies)[1] == 0:
            self.temps = time.clock()
            print("Nombre galaxies: "+str(self.val)+"; temps de construction des "+str(parametres.pasNbreNoeud)+" dernières galaxies: "+str(self.temps - self.tempsIni))
            self.tempsIni = self.temps
        return self.val
    def valeur(self):
        return self.val
    def noeudsGalaxie(self, n, L):
        self.compositionGalaxie[n]=L
        return len(L)

    def sauvegarde(self):
        dict = shelve.open(parametres.DirBD + '/listeGalaxies')
        x = 0 # changement dimanche 14
        while x < self.val:
            dict[str(x)] = self.compositionGalaxie[x]
            #print("galaxie sauvée: "+str(x))
            x +=1
        dict['nbreGalaxies'] = self.val
        dict.close()

    def rangement(self):
        tr = time.clock()
        print("         Extraction des galaxies terminées; opérations de rangement...")
        connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
        curseur2 = connexion.cursor()
        curseur2.execute('''INSERT INTO nombreGalaxies values (?)''', (str(self.val),))
        #connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
        print("Nombre de galaxies: "+str(self.val))
        #connexion.commit()
        t0 = tr
        i = 0
        while i < self.val:
            if divmod(i, parametres.pasGalaxies)[1] == 0 and i != 0:
                t1 = time.clock()
                print('Nombre galaxies rangées: '+str(i)+' sur '+str(self.val)+" ("+str(int((float(i)/float(self.val))*100))+'%) en '+format(t1 - t0,'f')+'sec.')
                t0 = t1
            lnoeuds = self.compositionGalaxie[i]
            n = len(lnoeuds)
            longueur = 0
            longueurMax = 0
            for texte in texteGalaxie(i, curseur2):
                longueur += len(texte)
                longueurMax = max(len(texte), longueurMax)
            curseur2.execute('''DELETE from degreGalaxies WHERE idGalaxie = ?''', (str(i),))
            curseur2.execute('''INSERT INTO degreGalaxies values (?,?, ?, ?,?)''', (str(i),str(n),str(longueur),str(int(longueur/n)),str(longueurMax,)))
            #connexion.commit()
            # print("degré galaxie n°"+str(i)+": "+str(n))
            i += 1
        connexion.commit()
        self.ajoutTexteNoeuds(connexion, curseur2)
        connexion.commit()
        connexion.close()
        trf = time.clock()
        print("             ... fin des opérations de rangements. Durée: "+format(trf - tr,'f')+" secondes")

    def ajoutTexteNoeuds(self, connexion, curseur):
        curseur.execute('''SELECT rowid, idRefSource, texteSource, ordonneeSource, empanSource,
        idRefCible, texteCible, ordonneeCible, empanCible from GrapheReutilisations''')
        curseurSource = connexion.cursor()
        curseurCible = connexion.cursor()
        X = curseur.fetchone()
        while X:
            curseurSource.execute('''SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = ?''', (str(X[0]),))
            curseurCible.execute('''SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = ?''', (str(X[0]),))
            self.miseAJourNoeud(curseurSource.fetchall()[0][0], X[1], X[2], X[3], X[4], curseurSource)
            self.miseAJourNoeud(curseurCible.fetchall()[0][0], X[5], X[6], X[7], X[8], curseurCible)
            X = curseur.fetchone()

    def miseAJourNoeud(self, Noeud, idRef, texte, ordonnee, empan, curseur):
        curseur.execute('''SELECT texte, ordonnee, empan FROM texteNoeuds WHERE idNoeud = ?''', (str(Noeud),))
        X = curseur.fetchall()
        if X:           
            if texte == X[0][0]:
                # print('le texte est le meme')
                return
            L = chaineMax(ordonnee, empan, texte, X[0][1], X[0][2], X[0][0])
            curseur.execute('''DELETE from texteNoeuds WHERE idNoeud = ?''', (str(Noeud),))
            #print("Texte ancien: "+str(X)+" - texte nouveau: (\""+str(texte)+"\","+str(ordonnee)+", "+str(empan)+") jointure: "+str(L[0]))
            curseur.execute('''INSERT INTO texteNoeuds values (?,?,?,?,?)''',
                            (str(Noeud), L[0], idRef, L[1], L[2],))
        else:
            curseur.execute('''INSERT INTO texteNoeuds values (?,?,?,?,?)''',(str(Noeud), texte, idRef, ordonnee, empan,))

def chaineMax(ordonnee1, empan1, texte1, ordonnee2, empan2, texte2):
    # print("texte1: "+texte1+" - texte2: "+texte2)
    # print("ordonnée1: "+str(ordonnee1)+" empan1: "+str(empan1))
    # print("ordonnée2: " + str(ordonnee2) + " empan2: " + str(empan2))
    if len(texte1) != empan1:
        #print("Erreur sur empan1"+" - Texte1: "+texte1+" - texte2: "+texte2)
        return chaineMax(ordonnee1, len(texte1), texte1, ordonnee2, empan2, texte2)
    elif len(texte2) != empan2:
        #print("Erreur sur empan2"+" - Texte1: "+texte1+" - texte2: "+texte2)
        return chaineMax(ordonnee1, empan1, texte1, ordonnee2, len(texte2), texte2)

    deltaInit = ordonnee2 - ordonnee1
    deltaFin = ordonnee2 + empan2 - ordonnee1 - empan1 -1
    #print("Delta fin: " + str(deltaFin)+" - "+"delta init: " + str(deltaInit))
    if deltaInit == 0:
        if deltaFin >= 0:
            return [texte2, ordonnee2, empan2]
        else:
            return [texte1, ordonnee1, empan1]
    elif deltaInit > 0:
        if deltaFin > 0:
            if texte1[deltaInit-1:] != texte2[:-deltaFin]:
                # print("ERREUR chevauchement= "+texte1[deltaInit-1:]+" - "+texte2[:-deltaFin]+"\n Texte1: "+texte1+" - texte2: "+texte2)
                # print("ordonnée1: "+str(ordonnee1)+" empan1: "+str(empan1))
                # print("ordonnée2: " + str(ordonnee2) + " empan2: " + str(empan2))
                # print("Résultats: "+texte1 + texte2[-deltaFin:])
                ecart = ajustement(texte1, ordonnee1, empan1, texte2, ordonnee2, empan2)
                #print("Ajustement: "+str(ecart))
                ordonnee2 = ordonnee2+ecart
                # print("Bout1 texte1: "+texte1[:ordonnee2-ordonnee1]+" bout2 texte1: "+texte1[ordonnee2-ordonnee1:])
                # print("Bout1 texte2: " + texte2[:empan1+ordonnee1-ordonnee2] + " bout2 texte2: " + texte2[empan1+ordonnee1-ordonnee2:])
                # print("Résultat: "+texte1 + texte2[-ordonnee2 + ordonnee1 + empan1:])
            return [texte1 + texte2[-ordonnee2 + ordonnee1 + empan1:], ordonnee1, ordonnee2 + empan2 - ordonnee1]
        else:
            return [texte1, ordonnee1, empan1]
    else:
        return chaineMax(ordonnee2, empan2, texte2, ordonnee1, empan1, texte1)


def ajustement(texte1, O1, E1, texte2, O2, E2):
    ecart = 1
    while ecart < O2-O1+max(E1,E2):
        d1 = O2-O1+ ecart
        f2 = O2 - O1 + ecart - E1
        d_1 = O2-O1-ecart
        f_2 = O2 - O1 - ecart - E1
        #print("Ecart = "+str(ecart)+" texte 1 \""+texte1[d1-1:]+"\" texte 2 \""+texte2[:-f2]+"\"")
        #print("Ecart = " + str(-ecart) + " texte 1 \"" + texte1[d_1-1:] + "\" texte 2 \"" + texte2[:-f_2]+"\"")
        if texte1[d1:] == texte2[:-f2]:
            return ecart
        elif texte1[d_1:] == texte2[:-f_2]:
            return -ecart
        ecart += 1
    print("Erreur ajustement: texte1="+texte1+" - O1="+str(O1)+" - E1="+str(E1)+ " - texte2="+texte2+" - O2="+str(O2)+" - E2="+str(E2))
    return 0


class noeudMarques():
    def __init__(self, max):
        self.noeuds = dict()
        self.maxNoeud = max
        n = 0
        while n < max:
            self.noeuds[n] = 'non'
            n += 1
    def noeudNonVisite(self, noeudCourant):
        n = noeudCourant
        while n < self.maxNoeud:
            if self.noeuds[n] == 'non':
                return n
            else:
                n += 1
        return None
    def affectationGalaxie(self,n, g):
        #print("Valeur appel affectation galaxie: "+str(n))
        if self.noeuds[n] != 'non':
            print("Erreur sur affectation galaxie au noeud "+str(n)+" - précédente affectation: "+str(self.noeuds[str(n)]))
            return 'erreur'
        else:
            self.noeuds[n] = g.val
    def galaxie(self,n):
        g = self.noeuds[n]
        if g == 'non':
            #print("Erreur sur consultation galaxie du noeud " + str(n))
            return 'erreur'
        else:
            return g



def extractionComposantesConnexes(maxNoeud):
    graphe = shelve.open(parametres.DirBD + '/liste_ajacence_graphe')
    graphe_t = shelve.open(parametres.DirBD + '/liste_ajacence_graphe_transpose')
    noeuds = noeudMarques(maxNoeud)
    Galaxie = galaxie()
    nouveauNoeud = noeuds.noeudNonVisite(0)
    while nouveauNoeud != None:# < maxNoeud:
        #L = composanteConnexe(nouveauNoeud, Galaxie, graphe, graphe_t, noeuds)
        #print("Nouveau noeud: "+str(nouveauNoeud)+" - galaxie: "+str(Galaxie.val))
        Galaxie.noeudsGalaxie(Galaxie.val, composanteConnexe(nouveauNoeud, Galaxie, graphe, graphe_t, noeuds))
        Galaxie.nouvelleValeur()
        nouveauNoeud = noeuds.noeudNonVisite(nouveauNoeud)
    graphe_t.close()
    graphe.close()
    Galaxie.sauvegarde()
    Galaxie.rangement()
    return Galaxie


def composanteConnexe(N, g, graphe, graphe_t, noeuds):
    E_noeuds = set()
    E_noeuds.add(N)
    noeudsVisites = set()
    while E_noeuds.__len__() != 0 :
        E_noeuds = E_noeuds.difference(noeudsVisites)
        #print("LNoeuds: "+str(E_noeuds)+"; noeuds visités: "+str(noeudsVisites))
        E = E_noeuds.pop()
        if not E in noeudsVisites:
            noeuds.affectationGalaxie(E, g)
            E_noeuds.update(fils(E, graphe, graphe_t))
            noeudsVisites.add(E)
        #print("E_noeuds = ", str(E_noeuds))
        #E_noeuds.remove(E)

        E_noeuds = E_noeuds.difference(noeudsVisites)
        #print("E-noeuds après: "+str(E_noeuds))
        if E_noeuds.intersection(noeudsVisites) != set():
            print("attention!! Noeud "+str(E))
        #if noeudsVisites == {}:
        #    print("Attention, noeud "+str(E))
    return noeudsVisites


def fils(X, graphe, graphe_t):
    return graphe[str(X)]+graphe_t[str(X)]

def extractionComposantesConnexes_(maxNoeud):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    #curseur.execute('''DROP INDEX idNoeud''')
    #curseur.execute('''CREATE INDEX idNoeud ON grapheGalaxies (idNoeudPere)''')
    noeuds = noeudMarques(maxNoeud)
    Galaxie = galaxie()
    tg1 = time.clock()
    nouveauNoeud = noeuds.noeudNonVisite(0)
    nbre_noeuds = 0
    nbre_noeuds_mod = 0

    while nouveauNoeud != None:# < maxNoeud:
        #L = composanteConnexe(nouveauNoeud, Galaxie, graphe, graphe_t, noeuds)
        #print("Nouveau noeud: "+str(nouveauNoeud)+" - galaxie: "+str(Galaxie.val))
        nbre_noeuds = nbre_noeuds + Galaxie.noeudsGalaxie(Galaxie.val, composanteConnexe_(nouveauNoeud, Galaxie, curseur, noeuds))
        if divmod(nbre_noeuds, parametres.pasNbreNoeudsGalaxie)[0] > nbre_noeuds_mod:
            nbre_noeuds_mod = divmod(nbre_noeuds, parametres.pasNbreNoeudsGalaxie)[0]
            tg2 = time.clock()
            print("Nombre total de nœuds traités: "+str(nbre_noeuds)+" - Nombre de galaxies construites: "+str(Galaxie.val)+" - temps: "+format(tg2 - tg1, 'f')+ " sec.")
            tg1 = tg2
        Galaxie.nouvelleValeur()
        nouveauNoeud = noeuds.noeudNonVisite(nouveauNoeud)
    Galaxie.sauvegarde()
    Galaxie.rangement()
    connexion.close()
    return Galaxie


def composanteConnexe_(N, g, curseur, noeuds):
    E_noeuds = set()
    E_noeuds.add(N)
    noeudsVisites = set()
    while E_noeuds.__len__() != 0:
        #E_noeuds = E_noeuds.difference(noeudsVisites)
        # print("LNoeuds: "+str(E_noeuds)+"; noeuds visités: "+str(noeudsVisites))
        E = E_noeuds.pop()
        if not E in noeudsVisites:
            noeuds.affectationGalaxie(E, g)
            #L = fils_(E, curseur)
            E_noeuds.update(fils_(E, curseur))
            noeudsVisites.add(E)
        # print("E_noeuds = ", str(E_noeuds))
        #E_noeuds.difference_update(noeudsVisites) ## Il me semble que l'on pourrait remplacer cela pour éviter de refaire une soustraction...
        #print("E-noeuds après: "+str(E_noeuds))
        # if E_noeuds.intersection(noeudsVisites) != set():
        #     print("attention!! Noeud "+str(E))
        # #if noeudsVisites == {}:
        # #    print("Attention, noeud "+str(E))
    return noeudsVisites

def degreGalaxie(G, curseur):
    curseur.execute('''SELECT degreGalaxie FROM degreGalaxies WHERE idGalaxie = (?)''', (G,))
    return curseur.fetchone()[0]

def fils_(X, curseur):
    curseur.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (X,))
    L = []
    # Q = curseur.fetchone()
    # while Q != None:
    #     L.append(Q[0])
    #     Q = curseur.fetchone()
    # return L
    for X in curseur.fetchall():
        L.append(X[0])
    return L


def cible(arc, curseur):
    curseur.execute('''SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = (?)''', (arc,))
    s = curseur.fetchall()
    #print("Ensemble des noeuds accessibles à partir de l'arc "+arc+": "+str(s))
    return s

def source(arc, curseur):
    curseur.execute('''SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = (?)''', (arc,))
    s = curseur.fetchall()
    #print("Ensemble des noeuds origines de l'arc " + arc + ": " + str(s))
    return s

def composantesExtraites():
    if 'listeGalaxies.db' in os.listdir(parametres.DirBD):
        dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
        return dirGalaxies['nbreGalaxies']
    else:
        return None


def textesGalaxie(numero):
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    textes = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT texte FROM texteNoeuds WHERE idNoeud = (?)''', (Noeud,))
        textes.add(curseur.fetchall()[0][0])
    connexion.close()
    return textes

# def texteGalaxie(numero, curseur):
#     dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
#     ListeNoeuds = dirGalaxies[str(numero)]
#     dirGalaxies.close()
#     textes = set()
#     for Noeud in ListeNoeuds:
#         curseur.execute('''SELECT texte FROM texteNoeuds WHERE idNoeud = (?)''', (Noeud,))
#         print(curseur.fetchall()) # ERREUR A CORRIGER!!!
#         #textes.add(curseur.fetchall()[0][0])
#     return textes
def texteGalaxie(numero, curseur):
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        #print("Noeud: "+str(Noeud[0])+" - arcs: "+str(L))
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        #print("Noeud: " + str(Noeud[0]) + " - arcs: " + str(L))
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    #print("Ensemble des réutilisations: "+ str(reutilisations))
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
    return textes


def auteursGalaxie(numero):
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    auteurs = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT auteur FROM texteNoeuds LEFT OUTER JOIN livres ON (livres.rowid = texteNoeuds.idRowLivre) WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()[0][0]
        if L != 'Inconnu':
            auteurs.add(L)
    connexion.close()
    return auteurs

def metaDonneesLivres(LNoeuds):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    metaDonnees = set()
    for Noeud in LNoeuds:
        curseur.execute(
            '''SELECT auteur, titre, date FROM texteNoeuds LEFT OUTER JOIN livres ON (livres.rowid = texteNoeuds.idRowLivre) WHERE idNoeud = (?)''',
            (Noeud,))
        LLivres = curseur.fetchall()[0]
        metaDonnees.add(LLivres)
    connexion.close()
    # print(metaDonnees)
    return metaDonnees

def metaDonnees(LNoeuds):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    metaDonnees = set()
    for Noeud in LNoeuds:
        curseur.execute(
            '''SELECT auteur, titre, date FROM texteNoeuds LEFT OUTER JOIN livres ON (livres.rowid = texteNoeuds.idRowLivre) WHERE idNoeud = (?)''',
            (Noeud,))
        LLivres = curseur.fetchall()
        curseur.execute(
            '''SELECT metaDataSource, metaDataCible FROM grapheGalaxiesSource LEFT OUTER JOIN grapheReutilisations ON (grapheReutilisations.rowid = grapheGalaxiesSource.idReutilisation) WHERE idNoeud = (?)''',
            (Noeud,))
        MetaData1 = curseur.fetchall()
        # print(MetaData1)
        curseur.execute(
            '''SELECT metaDataSource, metaDataCible FROM grapheGalaxiesCible LEFT OUTER JOIN grapheReutilisations ON (grapheReutilisations.rowid = grapheGalaxiesCible.idReutilisation) WHERE idNoeud = (?)''',
            (Noeud,))
        MetaData2 = curseur.fetchall()
        # print(MetaData2)
        MetaData = MetaData1 + MetaData2
        # print(MetaData)
        metaDonnees.add(LLivres[0]+MetaData[0])
    connexion.close()
    # print(metaDonnees)
    return metaDonnees

def galaxiesFiltre(requete):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    curseur.execute('''SELECT nbre FROM nombreGalaxies''')
    nombreTotalGalaxies = curseur.fetchall()[0][0]
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    numero = 0
    listeGalaxies = []
    listeGrossesGalaxies = dict()
    while numero < nombreTotalGalaxies:
        EnsNoeuds = dirGalaxies[str(numero)]
        if metaDonneesFiltreAux(EnsNoeuds, requete, curseur) :
            if len(EnsNoeuds) < parametres.tailleMinGrosseGalaxie :
                listeGalaxies.append(numero)
            else :
                tmp=amasFiltre(numero, requete, curseur)
                if tmp :
                    listeGrossesGalaxies[str(numero)]=tmp
        numero += 1
    listeGalaxiesTriee = sorted(listeGalaxies, key=lambda Galaxie: -degreGalaxie(Galaxie, curseur))
    if 'longueur_texte_maximal' in requete.keys():
        listeGalaxiesTriee = filtres.filtreLongueurMaximale(listeGalaxiesTriee, requete['longueur_texte_maximal'], curseur, dirGalaxies)    
        for gal in listeGrossesGalaxies :
            listeGrossesGalaxies[str(gal)] = filtres.filtreLongueurMaximale(listeGrossesGalaxies[str(gal)], requete['longueur_texte_maximal'], curseur, dirGalaxies)    
    dirGalaxies.close()
    connexion.close()
    return (listeGalaxiesTriee, listeGrossesGalaxies)

def amasFiltre(numGalaxie, requete, curseur) :
    dirAmas=shelve.open(parametres.DirBD + '/listeAmasGalaxie' + str(numGalaxie))
    res=[]
    for numero in range(len(dirAmas)-1):
        EnsNoeuds = dirAmas[str(numero)]
        if metaDonneesFiltreAux(EnsNoeuds, requete, curseur) :
            res.append(numero)
    dirAmas.close()
    return res

def galaxiesFiltreListe(Lrequete):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    curseur.execute('''SELECT nbre FROM nombreGalaxies''')
    nombreTotalGalaxies = curseur.fetchall()[0][0]
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    numero = 0
    listeGalaxies = []
    listeGrossesGalaxies = dict()
    while numero < nombreTotalGalaxies:
        EnsNoeuds = dirGalaxies[str(numero)]
        if metaDonneesFiltreListeAux(EnsNoeuds, Lrequete, curseur):
            if len(EnsNoeuds) < parametres.tailleMinGrosseGalaxie : 
                listeGalaxies.append(numero)
            else :
                tmp=amasFiltreListe(numero, Lrequete, curseur)
                if tmp :
                    listeGrossesGalaxies[str(numero)]=tmp
        numero += 1
    listeGalaxiesTriee = sorted(listeGalaxies, key=lambda Galaxie: -degreGalaxie(Galaxie, curseur))
    dirGalaxies.close()
    connexion.close()
    return (listeGalaxiesTriee, listeGrossesGalaxies)

def galaxiesFiltreListeAffiche(Lrequete):
    listeGalaxies = galaxiesFiltreListe(Lrequete)
    print("Il y a " + str(len(listeGalaxies)) + " satisfaisant à votre requête. Souhaitez-vous les afficher?")
    #print(listeGalaxies)
    G = lectureNumeroGalaxie(Lrequete,listeGalaxies)
    while G != False:
        texte=textesEtReferencesGalaxie(G)
        i=0
        print("Nombre total textes: ", len(texte), " - seuls les ", parametres.nombreGroupesImprimes, " seront imprimés.")
        while i < parametres.nombreGroupesImprimes and texte != set():
            print("- ",texte.pop())
            i+=1
        C = input("Souhaitez-vous sauver cette galaxie? ")
        if str.lower(C) in ["oui", "o", "y", "yes", "O", "Y", "Oui", "Yes"]:
           requete = filtres.choixRequeteSauvegarde(Lrequete)
        else:
            requete = False
        if requete == 0:
            visualisationGraphe.sauveGrapheGalaxie(G)
        elif requete != False:
            visualisationGraphe.sauveGrapheGalaxieAffichage(requete, G)
        print("Il y a ", len(listeGalaxies), " satisfaisant à votre requête. Souhaitez-vous en afficher certains?")
        G = lectureNumeroGalaxie(Lrequete, listeGalaxies)

def lectureNumeroGalaxie(Lrequete, listeGalaxies):
    C = input("Si oui, indiquez un nombre entre 1 et "+str(len(listeGalaxies))+", sinon 0: ")
    if not filtres.chaineChiffres(C) or int(C)> len(listeGalaxies):
        return lectureNumeroGalaxie(Lrequete, listeGalaxies)
    elif int(C) == 0:
        return False
    else:
        return listeGalaxies[int(C) - 1]

def galaxieFiltre(requete, numero):
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    return metaDonneesFiltre(ListeNoeuds, requete)

def galaxieFiltreListe(Lrequete, numero):
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    satifactionRequete = metaDonneesFiltreListeAux(ListeNoeuds, Lrequete, curseur)
    connexion.close()
    return satifactionRequete


def metaDonneesFiltre(EnsNoeuds, requete):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    satifactionRequete = metaDonneesFiltreAux(EnsNoeuds, requete, curseur)
    connexion.close()
    return satifactionRequete

def metaDonneesFiltreAux(EnsNoeuds, requete, curseur):
    if 'nbre_minimal_noeuds' in requete.keys() and requete['nbre_minimal_noeuds']> len(EnsNoeuds):
        return False
    for Noeud in EnsNoeuds:
        curseur.execute(
            '''SELECT auteur, titre, date, empan FROM texteNoeuds LEFT OUTER JOIN livres ON (livres.rowid = texteNoeuds.idRowLivre) WHERE idNoeud = (?)''',
            (Noeud,))
        LLivres = curseur.fetchall()[0]
        # print("Livres: "+str(LLivres))
        # print("Requête: "+str(requete)+" - satifaction requête livres: "+str(filtreLivres(requete, LLivres)))

        if filtres.filtreLivres(requete, LLivres):
            curseur.execute(
                '''SELECT metaDataSource, metaDataCible FROM grapheGalaxiesSource LEFT OUTER JOIN grapheReutilisations ON (grapheReutilisations.rowid = grapheGalaxiesSource.idReutilisation) WHERE idNoeud = (?)''',(Noeud,))
            MetaData1 = curseur.fetchall()
            curseur.execute(
                '''SELECT metaDataSource, metaDataCible FROM grapheGalaxiesCible LEFT OUTER JOIN grapheReutilisations ON (grapheReutilisations.rowid = grapheGalaxiesCible.idReutilisation) WHERE idNoeud = (?)''',
                (Noeud,))
            MetaData2 = curseur.fetchall()
            MetaData = MetaData1 + MetaData2
            #print("Requête: " + str(requete) + " - satifaction requête métadata: " + str(filtreMetaData(requete, MetaData[0])))
            if filtres.filtreMetaData(requete, MetaData[0]):
                return True
    return False

def metaDonneesFiltreListeAux(EnsNoeuds, Lrequete, curseur):
    for n in range(len(Lrequete)):
        if not metaDonneesFiltreAux(EnsNoeuds, Lrequete[n], curseur):
            return False
    return True

def amasFiltreListe(numGalaxie, Lrequete, curseur) :
    dirAmas=shelve.open(parametres.DirBD + '/listeAmasGalaxie' + str(numGalaxie))
    res=[]
    for numero in range(len(dirAmas)):
        EnsNoeuds = dirAmas[str(numero)]
        if metaDonneesFiltreListeAux(EnsNoeuds, Lrequete, curseur) :
            res.append(numero)
    dirAmas.close()
    return res

# def presenceAuteurGalaxieListeNoeuds(auteur, listeNoeuds):
#     connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
#     curseur = connexion.cursor()
#     reutilisations = set()
#     for Noeud in listeNoeuds:
#         curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
#         L = curseur.fetchall()
#         if L != []:
#             reutilisations.add(L[0][0])
#         curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
#         L = curseur.fetchall()
#         # print("Noeud: " + str(Noeud[0]) + " - arcs: " + str(L))
#         if L != []:
#             reutilisations.add(L[0][0])
#     # print("Ensemble des réutilisations: "+ str(reutilisations))
#     for idReutilisation in reutilisations:
#         curseur.execute('''SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?)''',
#                         (str(idReutilisation),))
#         t1 = curseur.fetchall()[0]
#         curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
#         if auteur in str.lower(curseur.fetchall()[0][0]):
#             return auteur
#         curseur.execute('''SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?)''',
#                         (str(idReutilisation),))
#         t1 = curseur.fetchall()[0]
#         curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
#         if auteur in str.lower(curseur.fetchall()[0][0]):
#             return auteur
#     connexion.close()
#     return ()
#
# def presenceLNomAuteurGalaxieListeNoeuds(LAuteurs, listeNoeuds):
#     connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
#     curseur = connexion.cursor()
#     reutilisations = set()
#     for Noeud in listeNoeuds:
#         curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
#         L = curseur.fetchall()
#         if L != []:
#             reutilisations.add(L[0][0])
#         curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
#         L = curseur.fetchall()
#         # print("Noeud: " + str(Noeud[0]) + " - arcs: " + str(L))
#         if L != []:
#             reutilisations.add(L[0][0])
#     # print("Ensemble des réutilisations: "+ str(reutilisations))
#     for idReutilisation in reutilisations:
#         curseur.execute('''SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?)''',
#                         (str(idReutilisation),))
#         t1 = curseur.fetchall()[0]
#         curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
#         if toutDans(LAuteurs, str.lower(curseur.fetchall()[0][0])):
#             return LAuteurs
#         curseur.execute('''SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?)''',
#                         (str(idReutilisation),))
#         t1 = curseur.fetchall()[0]
#         curseur.execute('''SELECT auteur FROM livres WHERE rowid = (?)''', (t1[0],))
#         if toutDans(LAuteurs, str.lower(curseur.fetchall()[0][0])):
#             return LAuteurs
#     connexion.close()
#     return ()

def toutDans(L, F):
    for X in L:
        if X not in F:
            return ()
    return L


# def galaxiesAuteur(Auteur):
#     nomAuteur = str.lower(Auteur)
#     dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
#     nbreGalaxies = dirGalaxies['nbreGalaxies']
#
#     listeGalaxiesAuteur=[]
#     for X in range(0, nbreGalaxies):
#         if presenceAuteurGalaxieListeNoeuds(nomAuteur, dirGalaxies[str(X)]):
#             listeGalaxiesAuteur.append(X)
#     dirGalaxies.close()
#     return listeGalaxiesAuteur

# def galaxiesListeNomsAuteur(LNomsAuteur):
#     LNomsAuteurMin = []
#     for nomAuteur in LNomsAuteur:
#         LNomsAuteurMin.append(str.lower(nomAuteur))
#     dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
#     nbreGalaxies = dirGalaxies['nbreGalaxies']
#     listeGalaxiesAuteur=[]
#     for X in range(0, nbreGalaxies):
#         if presenceLNomAuteurGalaxieListeNoeuds(LNomsAuteurMin, dirGalaxies[str(X)]):
#             listeGalaxiesAuteur.append(X)
#     dirGalaxies.close()
#     return listeGalaxiesAuteur
#
# def galaxiesListesNomsAuteurs(LNomsAuteurs): # ATTENTION, L'ARGUMENT EST UNE LISTE DE LISTES
#     LNomsAuteursMin = []
#     for nomsAuteur in LNomsAuteurs:
#         LNomsAuteurMin=[]
#         for nomAuteur in nomsAuteur:
#             LNomsAuteurMin.append(str.lower(nomAuteur))
#         LNomsAuteursMin.append(LNomsAuteurMin)
#     dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
#     nbreGalaxies = dirGalaxies['nbreGalaxies']
#     listeGalaxiesAuteur=[]
#     for X in range(0, nbreGalaxies):
#         LNoeuds = dirGalaxies[str(X)]
#         if presenceAuteursListeNoeuds(LNomsAuteursMin, LNoeuds):
#             listeGalaxiesAuteur.append(X)
#     dirGalaxies.close()
#     return listeGalaxiesAuteur
#
# def presenceAuteursListeNoeuds(LNomsAuteurs, LNoeuds):
#     for LNomsAuteurMin in LNomsAuteurs:
#         if not presenceLNomAuteurGalaxieListeNoeuds(LNomsAuteurMin, LNoeuds):
#             return ()
#     return True

def ordonner(LGalaxies):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    L=sorted(LGalaxies,key= lambda Galaxie: -degreGalaxie(Galaxie, curseur))
    return L
    connexion.close()


# def galaxiesAuteurOrdonnees(Auteur):
#     return ordonner(galaxiesAuteur(Auteur))
#
# def galaxiesNomsAuteurOrdonnees(LNomsAuteur):
#     return ordonner(galaxiesListeNomsAuteur(LNomsAuteur))
#
# def galaxiesNomsAuteursOrdonnees(LNomsAuteurs):
#     return ordonner(galaxiesListesNomsAuteurs(LNomsAuteurs))
#
#
# def presenceMotTitreGalaxieListeNoeuds(Mot, listeNoeuds):
#     connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
#     curseur = connexion.cursor()
#     reutilisations = set()
#     for Noeud in listeNoeuds:
#         curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
#         L = curseur.fetchall()
#         if L != []:
#             reutilisations.add(L[0][0])
#         curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
#         L = curseur.fetchall()
#         # print("Noeud: " + str(Noeud[0]) + " - arcs: " + str(L))
#         if L != []:
#             reutilisations.add(L[0][0])
#     # print("Ensemble des réutilisations: "+ str(reutilisations))
#     for idReutilisation in reutilisations:
#         curseur.execute('''SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?)''',
#                         (str(idReutilisation),))
#         t1 = curseur.fetchall()[0]
#         curseur.execute('''SELECT titre FROM livres WHERE rowid = (?)''', (t1[0],))
#         if Mot in str.lower(curseur.fetchall()[0][0]):
#             return Mot
#         curseur.execute('''SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?)''',
#                         (str(idReutilisation),))
#         t1 = curseur.fetchall()[0]
#         curseur.execute('''SELECT titre FROM livres WHERE rowid = (?)''', (t1[0],))
#         if Mot in str.lower(curseur.fetchall()[0][0]):
#             return Mot
#     connexion.close()
#     return ()
#
# def galaxiesTitreMot(Mot):
#     nomMot = str.lower(Mot)
#     dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
#     nbreGalaxies = dirGalaxies['nbreGalaxies']
#
#     listeGalaxiesMot=[]
#     for X in range(0, nbreGalaxies):
#         if presenceMotTitreGalaxieListeNoeuds(nomMot, dirGalaxies[str(X)]):
#             listeGalaxiesMot.append(X)
#     dirGalaxies.close()
#     return listeGalaxiesMot
#
#
# def presenceAuteurGalaxie(nom, Galaxie):
#     S = auteursGalaxie(Galaxie)
#     for X in S:
#         #print('- '+str.lower(X))
#         if nom in str.lower(X):
#             return nom
#     return ()


def textesEtReferencesGalaxie(numero):
    dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
    # print('Clefs des galaxies: ')
    # print(list(dirGalaxies.keys()))

    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        #print("Noeud: "+str(Noeud[0])+" - arcs: "+str(L))
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        #print("Noeud: " + str(Noeud[0]) + " - arcs: " + str(L))
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    #print("Ensemble des réutilisations: "+ str(reutilisations))
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0],curseur.fetchall()[0]))
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0]))
    connexion.close()
    return textes


def textesListeNoeuds(ListeNoeuds):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    textes = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT texte FROM texteNoeuds WHERE idNoeud = (?)''', (Noeud,))
        textes.add(curseur.fetchall()[0][0])
    connexion.close()
    return textes


def textesEtReferencesListeNoeuds(ListeNoeuds):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        #print("Noeud: "+str(Noeud[0])+" - arcs: "+str(L))
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        #print("Noeud: " + str(Noeud[0]) + " - arcs: " + str(L))
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    #print("Ensemble des réutilisations: "+ str(reutilisations))
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0],curseur.fetchall()[0]))
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0]))
    connexion.close()
    return textes

def textesEtReferencesListeNoeuds_avecNoeuds(ListeNoeuds):
    connexion = sqlite3.connect(parametres.DirBD + '/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        #print("Noeud: "+str(Noeud[0])+" - arcs: "+str(L))
        if L != []:
            reutilisations.add((L[0][0],Noeud))
        curseur.execute('''SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        #print("Noeud: " + str(Noeud[0]) + " - arcs: " + str(L))
        if L != []:
            reutilisations.add((L[0][0], Noeud))
    textes = set()
    #print("Ensemble des réutilisations: "+ str(reutilisations))
    for idReutilisation in reutilisations:
        curseur.execute('''SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation[0]),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0],curseur.fetchall()[0], idReutilisation[1]))
        curseur.execute('''SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?)''', (str(idReutilisation[0]),))
        t1 = curseur.fetchall()[0]
        curseur.execute('''SELECT auteur, titre, date FROM livres WHERE rowid = (?)''', (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0],idReutilisation[1]))
    connexion.close()
    return textes

