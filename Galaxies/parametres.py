#!/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Jean-Gabriel Ganascia'

import lecture_fic

NombreLignes = 0

DirGlobal = "./resultat_Galaxies/"
DirFichier= "./Tab"
lecture_fic.rechercheDossiersBDsAmasetGraphes(DirGlobal)
DirBD = DirGlobal+'BDs'
DirAmas = DirGlobal+'amas'
DirGraphes = DirGlobal+'graphes'
DirJson = DirGlobal+"jsons/"
DirAffichage = "./gen-louvain/"
DirPgm=DirAffichage
DirLouvain = ";/gen-louvain"

pasTracage = 100000
pasNbreNoeud = 10000
pasGalaxies = 10000
pasNbreNoeudsGalaxie = 10000

# metaDataSource = 'source_generatedclass'
# metaDataSourceType = 'TEXT'
# metaDataCible = 'target_birth'
# metaDataCibleType = 'NUM'
metaDataSource = 'source_text_genre'
metaDataSourceType = 'TEXT'
metaDataCible = 'target_subject'
metaDataCibleType = 'TEXT'

#largeurAjustement = 30
tailleMinGrosseGalaxie = 300
nombreGroupesImpriymes = 10
