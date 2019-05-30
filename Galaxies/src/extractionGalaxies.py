#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import amas
import baseDonnees
import filtres
import re
import shelve
import sqlite3
import time


class galaxie:  # permet d'énumérer composantes connexes

    def __init__(self, project_path, max_length_galaxie):
        self.val = 0
        self.compositionGalaxie = dict()
        self.tempsIni = time.clock()
        self.pasGalaxies = 10000
        self.pasNbreNoeud = 10000
        self.max_length_galaxie = max_length_galaxie
        self.project_path = project_path
        self.data_base_path = project_path + '/BDs'

    def nouvelleValeur(self):
        self.val += 1
        if divmod(self.val, self.pasGalaxies)[1] == 0:
            self.temps = time.clock()
            print("Nombre galaxies: " + str(self.val) + "; temps de construction des " + str(
                self.pasNbreNoeud) + " dernières galaxies: " + str(self.temps - self.tempsIni))
            self.tempsIni = self.temps
        return self.val

    def valeur(self):
        return self.val

    def noeudsGalaxie(self, n, L):
        self.compositionGalaxie[str(n)] = L
        return len(L)

    def add_galaxie(self, id_galaxie, nodes_list):
        self.compositionGalaxie[str(id_galaxie)] = nodes_list

    def sauvegarde(self):
        list_galaxies = shelve.open(self.data_base_path + '/listeGalaxies')
        connexion = sqlite3.connect(self.data_base_path + '/galaxie.db', 1, 0, 'EXCLUSIVE')
        cursor = connexion.cursor()
        x = 0
        for id_galaxie in range(self.val):

            list_galaxies[str(id_galaxie)] = self.compositionGalaxie[str(id_galaxie)]
            x += 1
            if len(self.compositionGalaxie[str(id_galaxie)]) > self.max_length_galaxie:
                print('id_galaxie =', id_galaxie, ' ; self.compositionGalaxie[str(id_galaxie)] =',
                      self.compositionGalaxie[str(id_galaxie)])
                list_amas = amas.create_partition(self.compositionGalaxie[str(id_galaxie)], self.project_path)
                print(list_amas)
                while any([len(list_amas[ama]) > self.max_length_galaxie for ama in list_amas]):
                    list_amas_temp = dict()
                    i = len(list_amas)
                    for ama in list_amas:
                        if len(list_amas[ama]) > self.max_length_galaxie:
                            list_amas_split = amas.create_partition(list_amas[ama], self.project_path)
                            for sub_ama in list_amas_split:
                                list_amas_temp[ama + i] = list_amas_split[sub_ama]
                                i += 1
                        else:
                            list_amas_temp[ama] = list_amas[ama]

                    list_amas = list_amas_temp

                for id_partition in list_amas:
                    ama_name = str(id_galaxie) + '-' + str(id_partition)
                    list_galaxies[ama_name] = list_amas[id_partition]
                    self.add_galaxie(ama_name, list_amas[id_partition])
                    x += 1

        self.val = x
        list_galaxies.close()

    def rangement(self):
        tr = time.clock()
        print("         Extraction des galaxies terminées; opérations de rangement...")
        connexion = sqlite3.connect(self.data_base_path + '/galaxie.db', 1, 0, 'EXCLUSIVE')
        cursor = connexion.cursor()
        cursor.execute('''INSERT INTO nombreGalaxies values (?)''', (str(self.val),))
        print("Nombre de galaxies: " + str(self.val))
        self.ajoutTexteNoeuds(connexion, cursor)
        t0 = tr
        i = 0
        for galaxie in self.compositionGalaxie:
            if divmod(i, 1000)[1] == 0 and i != 0:
                connexion.commit()
                t1 = time.clock()
                print('Nombre galaxies rangées: ' + str(i) + ' sur ' + str(self.val) + " (" + str(
                    int((float(i) / float(self.val)) * 100)) + '%) en ' + format(t1 - t0, 'f') + 'sec.')
                t0 = t1
            list_nodes = self.compositionGalaxie[galaxie]
            add_nodes_database(cursor, list_nodes, galaxie)
            n = len(list_nodes)
            longueur = 0
            longueurMax = 0
            for texte in texteGalaxie(galaxie, cursor, self.data_base_path):
                longueur += len(texte)
                longueurMax = max(len(texte), longueurMax)
            cursor.execute('''DELETE from degreGalaxies WHERE idGalaxie = ?''', (str(galaxie),))
            cursor.execute('''INSERT INTO degreGalaxies values (?, ?, ?, ?, ?)''',
                             (str(galaxie), str(n), str(longueur), str(int(longueur / n)), str(longueurMax, )))
            if int(longueur / n) > longueurMax:
                print("ERROR : average length > max length, galaxie =", galaxie)
            i += 1

        connexion.commit()
        connexion.close()
        trf = time.clock()
        print("             ... fin des opérations de rangements. Durée: " + format(trf - tr, 'f') + " secondes")

    def ajoutTexteNoeuds(self, connexion, curseur):
        curseur.execute('''SELECT rowid, idRefSource, texteSource, ordonneeSource, empanSource,
        idRefCible, texteCible, ordonneeCible, empanCible from GrapheReutilisations''')
        curseurSource = connexion.cursor()
        curseurCible = connexion.cursor()
        node = curseur.fetchone()
        while node:
            curseurSource.execute('''SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = ?''',
                                  (str(node[0]),))
            curseurCible.execute('''SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = ?''',
                                 (str(node[0]),))
            update_node(curseurSource.fetchall()[0][0], node[1], node[2], node[3], node[4], curseurSource)
            update_node(curseurCible.fetchall()[0][0], node[5], node[6], node[7], node[8], curseurCible)
            node = curseur.fetchone()
        # curseur.execute('''SELECT idNoeud from ListeNoeuds''')
        # EnsembleNoeuds = set(curseur.fetchall())


def add_nodes_database(cursor, list_nodes, galaxie_id):
    for node in list_nodes:
        cursor.execute('''SELECT texte, idRowLivre, ordonnee, empan FROM ListeNoeuds WHERE idNoeud = ?''', (node,))
        merge_node = []
        for n in cursor.fetchall():
            new_node = [n[0], n[1], n[2], n[3]]
            if new_node not in merge_node:
                merge_node.append(new_node)
        if len(merge_node) > 1:
            new_node = merge_nodes(merge_node)
        cursor.execute('''INSERT INTO texteNoeuds values (?,?,?,?,?,?)''', (str(node), new_node[0], new_node[1],
                                                                            new_node[2], new_node[3], galaxie_id))


def update_node(node, idRef, text, ordonnee, empan, cursor):
    cursor.execute('''INSERT INTO listeNoeuds values (?,?,?,?,?)''', (str(node), text, idRef, ordonnee, len(text),))


def merge_nodes(list_node):
    list_node_sort = sorted(list_node, key=lambda x: x[2])
    new_node = list_node_sort[0]
    for i in range(1, len(list_node_sort)):
        new_node[0] = merge_text(new_node[0], list_node_sort[i][0])
    return [new_node[0], new_node[1], new_node[2], len(new_node[0])]


def merge_text(text1, text2):
    if text2 in text1:
        return text1
    i = 0
    while i < len(text1):
        if text1[i] == text2[0]:
            if i == len(text1) - 1:
                return text1[:-1] + text2
            if text1[i:] == text2[:len(text1) - i]:
                return text1[:i] + text2
        i += 1
    print("ERROR : text 1 :", text1, '\nand text 2 have nothing in commun :', text2)

    return text1 + text2


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

    def affectationGalaxie(self, n, g):
        # print("Valeur appel affectation galaxie: "+str(n))
        if self.noeuds[n] != 'non':
            print("Erreur sur affectation galaxie au noeud " + str(n) + " - précédente affectation: " + str(
                self.noeuds[str(n)]))
            return 'erreur'
        else:
            self.noeuds[n] = g.val

    def galaxie(self, n):
        g = self.noeuds[n]
        if g == 'non':
            # print("Erreur sur consultation galaxie du noeud " + str(n))
            return 'erreur'
        else:
            return g


def extractionComposantesConnexes(maxNoeud, project_path, max_length_galaxie, step=10000):

    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    curseur = connexion.cursor()
    noeuds = noeudMarques(maxNoeud)
    Galaxie = galaxie(project_path, max_length_galaxie)
    tg1 = time.clock()
    nouveauNoeud = noeuds.noeudNonVisite(0)
    nbre_noeuds = 0
    nbre_noeuds_mod = 0

    while nouveauNoeud is not None:  # < maxNoeud:

        nbre_noeuds = nbre_noeuds + Galaxie.noeudsGalaxie(Galaxie.val,
                                                          _composanteConnexe(nouveauNoeud, Galaxie, curseur, noeuds))
        if divmod(nbre_noeuds, step)[0] > nbre_noeuds_mod:
            nbre_noeuds_mod = divmod(nbre_noeuds, step)[0]
            tg2 = time.clock()
            print("Nombre total de nœuds traités: " + str(nbre_noeuds) + " - Nombre de galaxies construites: " + str(
                Galaxie.val) + " - temps: " + format(tg2 - tg1, 'f') + " sec.")
            tg1 = tg2
        Galaxie.nouvelleValeur()
        nouveauNoeud = noeuds.noeudNonVisite(nouveauNoeud)
    Galaxie.sauvegarde()
    Galaxie.rangement()
    connexion.close()
    return Galaxie


def _composanteConnexe(N, g, curseur, noeuds):
    E_noeuds = set()
    E_noeuds.add(N)
    noeudsVisites = set()
    while E_noeuds.__len__() != 0:
        E = E_noeuds.pop()
        if not E in noeudsVisites:
            noeuds.affectationGalaxie(E, g)
            E_noeuds.update(_fils(E, curseur))
            noeudsVisites.add(E)
    return noeudsVisites


def degreGalaxie(idGalaxie, cursor, select_item="degreGalaxie"):
    """
        Function that execute a query on cursor, for knowing the degre, number of node, of Galaxie idGalaxie

    :param idGalaxie:
    :param cursor: The id of the Galaxie we want meta-data
    :param select_item:
    :return: The degre of idGalaxie
    """
    query = "SELECT {} FROM degreGalaxies WHERE idGalaxie = '{}'".format(select_item, idGalaxie)
    cursor.execute(query)
    return cursor.fetchone()[0]


def get_meta_data_from_idGalaxie(project_path, idGalaxie):
    """
        Function that connects to the data base, and extracts and returns meta information about a specific Galaxie

    :param project_path: The path of the project
    :param idGalaxie: The id of the Galaxie we want meta-data
    :return: The line in table degreGalaxies that corresponding to the Galaxie Id
    """
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')  # Connection to the DB
    cursor = connexion.cursor()  # Creation of cursor
    cursor.execute('''SELECT * FROM degreGalaxies WHERE idGalaxie = (?)''',
                   (idGalaxie,))  # Query execution that collecte meta-data on idGalaxie
    result = cursor.fetchone()  # We take the first result, there must be only one result
    connexion.close()
    return result


def _fils(X, curseur):
    curseur.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (X,))
    L = []
    for X in curseur.fetchall():
        L.append(X[0])
    return L


def get_graph_from_nodes(nodes_list, cursor):
    graph = {}
    for node in nodes_list:
        cursor.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (node,))
        child_list = cursor.fetchall()
        if child_list != []:
            graph[node] = set()
        for child in child_list:
            graph[node].add(child[0])
    return graph


def texteGalaxie(numero, curseur, data_base_path):
    dirGalaxies = shelve.open(data_base_path + '/listeGalaxies')
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    textes = list()
    for Noeud in ListeNoeuds:
        curseur.execute('''SELECT texte FROM texteNoeuds WHERE idNoeud = (?)''', (Noeud,))
        L = curseur.fetchall()
        textes.append(L[0][0])
    return textes


def update_query_table(cursor, galaxies_list):
    baseDonnees.reload_query_table(cursor)
    for galaxie in galaxies_list:
        cursor.execute('''INSERT INTO Query values (?,?)''', (galaxie, False,))


def mark_galaxie_query_table(project_path, id_galaxie):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    cursor.execute('''SELECT mark from Query WHERE idGalaxie = ?''', (id_galaxie,))
    is_marked = not (cursor.fetchone()[0])
    cursor.execute('''UPDATE Query SET mark = (?) WHERE idGalaxie = (?)''', (is_marked, id_galaxie,))
    connexion.commit()
    connexion.close()


def galaxies_filter(query, project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    dirGalaxies = shelve.open(project_path + '/BDs/listeGalaxies')
    list_galaxies = []

    for id_galaxie in dirGalaxies:
        nodes_list = dirGalaxies[id_galaxie]
        append = True
        for num_query in query:
            if not metaDonneesFiltreAux(nodes_list, query[num_query], cursor):
                append = False
                break
        if append:
            list_galaxies.append(id_galaxie)

    update_query_table(cursor, list_galaxies)

    dirGalaxies.close()
    connexion.commit()
    connexion.close()
    return list_galaxies


def nodes_filter(filter_, project_path):

    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor_query = connexion.cursor()
    cursor_node = connexion.cursor()
    cursor = connexion.cursor()

    cursor_query.execute('''SELECT idGalaxie FROM Query''')
    galaxies_query = cursor_query.fetchone()

    while galaxies_query:

        cursor_node.execute('''SELECT idNoeud, auteur, titre, date, empan, texte FROM texteNoeuds LEFT OUTER JOIN livres
         ON (livres.rowid = texteNoeuds.idRowLivre) WHERE texteNoeuds.idGalaxie = (?)''', galaxies_query)

        node = cursor_node.fetchone()
        while node:
            if filtres.filtreLivres(filter_, node[1:]):
                cursor.execute('''INSERT INTO Filter values (?,?)''', (node[0], galaxies_query))
            node = cursor_node.fetchone()
        galaxies_query = cursor_query.fetchone()

    connexion.commit()
    connexion.close()
    return

    # node = cursor.fetchone()
    # while node:
    #     node = cursor.fetchone()
    # for id_galaxie in dirGalaxies:
    #     nodes_list = dirGalaxies[id_galaxie]
    #     append = True
    #     for num_query in query:
    #         if not metaDonneesFiltreAux(nodes_list, query[num_query], cursor):
    #             append = False
    #             break
    #     if append:
    #         list_galaxies.append(id_galaxie)
    #
    # update_query_table(cursor, list_galaxies)
    #
    # dirGalaxies.close()
    # return list_galaxies


def metaDonneesFiltreAux(EnsNoeuds, requete, curseur):
    if 'nbre_minimal_noeuds' in requete.keys() and requete['nbre_minimal_noeuds'] > len(EnsNoeuds):
        return False
    if 'nbre_maximal_noeuds' in requete.keys() and requete['nbre_maximal_noeuds'] < len(EnsNoeuds):
        return False

    long_enough = True
    long_comparator = -1
    if 'longueur_texte_maximal' in requete.keys():
        long_enough = False
        long_comparator = requete['longueur_texte_maximal']

    filtre = False

    for Noeud in EnsNoeuds:
        curseur.execute(
            '''SELECT auteur, titre, date, empan FROM texteNoeuds LEFT OUTER JOIN livres ON (livres.rowid = texteNoeuds.idRowLivre) WHERE idNoeud = (?)''',
            (Noeud,))
        LLivres = curseur.fetchall()[0]
        if LLivres[3] >= long_comparator:
            long_enough = True
        if filtres.filtreLivres(requete, LLivres):
            filtre = True
        if filtre and long_enough:
            return True
    return False


def get_list_galaxie(project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    cursor.execute(
        '''SELECT Query.idGalaxie, degreGalaxie, mark FROM Query LEFT OUTER JOIN degreGalaxies 
            ON (Query.idGalaxie = degreGalaxies.idGalaxie)''')
    result = [id_galaxie for id_galaxie in cursor.fetchall()]
    connexion.close()
    return result


def sort_list_galaxie(project_path, table_index=0):
    """
        Function that sorts galaxie list of the last query, on a criteria according to the table_index :
            0 idGalaxie
            1 degreGalaxie
            2 longueurTexteTotale
            3 longueurTexteMoyenne
            4 longueurTexteMax
        that is base on the degreGalaxies table

    :param project_path:
    :param table_index:
    :return:
    """
    galaxies_list = get_list_galaxie(project_path)
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    select_item = {0: 'idGalaxie', 1: 'degreGalaxie', 2: 'longueurTexteTotale', 3: 'longueurTexteMoyenne',
                   4: 'longueurTexteMax'}
    result = sorted(galaxies_list, key=lambda Galaxie: degreGalaxie(Galaxie[0], cursor, select_item[table_index]))
    connexion.close()
    return result


def get_int(id_galaxie):
    """
        Function that is aim for give a order in id_galaxie name. Because an id is a number like 425 or a ama number
    such as 9-12, we can not just use int() operator

    :param id_galaxie: The id of a galaxie
    :return: A tuple that is the number of the galaxie and then the ama that is correspond, e.g. 9-12 become (9,12).
            Or for a unique galaxie it is (425,-1)
    """
    if "-" in id_galaxie:  # if we are manipulating an ama
        number_ama = re.findall(r'\d+', id_galaxie)
        return int(number_ama[0]), int(number_ama[1])
    return int(id_galaxie), -1
