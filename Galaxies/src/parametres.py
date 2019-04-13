#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import lecture_fic

NombreLignes = 0

DirProject = ""
DirBD = DirProject+'BDs'
DirAmas = DirProject+'amas'
DirGraphes = DirProject+'graphs'
DirJson = DirProject+"jsons/"
DirAffichage = "./gen-louvain/"
DirPgm=DirAffichage
DirLouvain = "./gen-louvain"

def set_DirProject(newDirProject):
    DirProject = newDirProject
    DirBD = DirProject + 'BDs'
    DirAmas = DirProject + 'amas'
    DirGraphes = DirProject + 'graphes'
    DirJson = DirProject + "jsons/"


pasTracage = 100000
pasNbreNoeud = 10000
pasGalaxies = 10000
pasNbreNoeudsGalaxie = 10000

metaDataSource = 'source_text_genre'
metaDataSourceType = 'TEXT'
metaDataCible = 'target_subject'
metaDataCibleType = 'TEXT'

#largeurAjustement = 30
tailleMinGrosseGalaxie = 300
nombreGroupesImpriymes = 10
