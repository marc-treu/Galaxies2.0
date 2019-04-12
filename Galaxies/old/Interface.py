#!/bin/env python
# -*- coding: utf-8 -*-
# from datetime import time

import tkinter as tk
from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from tkinter.simpledialog import *

import parametres
import os
import re
import shelve
import javaVisualisation



def repeat():
    root = Tk()
    root.withdraw()
    res = askyesno('Nouvelle requête', 'Souhaitez-vous ajouter une nouvelle requête ?')
    root.destroy()
    return res


def subSort():
    root = Tk()
    root.withdraw()
    res = askyesno('Trier les sous-amas', 'Certains amas ont plus de ' + str(
        parametres.tailleMinGrosseGalaxie) + ' noeuds.\nSouhaitez-vous en extraire les sous-amas ?')
    root.destroy()
    return res




def recupereRequete():
    def recupere():
        if (auteur.get()):
            requete['auteur'] = auteur.get().split()
        if (notauteur.get()):
            requete['-auteur'] = notauteur.get().split()
        if (mcles.get()):
            requete['mots_titre'] = mcles.get().split()
        if (notmcles.get()):
            requete['-mots_titre'] = notmcles.get().split()
        if (date.get()):
            requete['date'] = [int(s) for s in date.get().split() if s.isdigit()]
            if (len(requete['date']) == 0):
                del requete['date']
            elif (len(requete['date']) == 1):
                i = 1
                while (date.get()[i] == ' '):
                    i = i + 1
                if (date.get()[i] == '-'):
                    requete['date'].insert(0, "-")
                else:
                    requete['date'].append("-")
            elif (len(requete['date']) == 0):
                print("Erreur à la déclaration de l'intervalle")
            elif requete['date'][0] > requete['date'][1]:
                print(
                    "Erreur dans la déclaration de l'intervalle\nDonner en premier argument une date antérieure à la seconde")
        if (empan.get()):
            requete['empan'] = [int(s) for s in empan.get().split() if s.isdigit()].pop()
        if (ltexte_max.get()):
            requete['longueur_texte_maximal'] = [int(s) for s in ltexte_max.get().split() if s.isdigit()].pop(0)
        if (nbnoeuds_min.get()):
            requete['nbre_minimal_noeuds'] = [int(s) for s in nbnoeuds_min.get().split() if s.isdigit()].pop(0)
        fenetre.destroy()

    dict_requetes = dict()
    i = 0

    while (repeat()):
        # Tk().withdraw()
        fenetre = tkinter.Tk()
        fenetre.title("Recherche dans les galaxies")
        fenetre.geometry("800x350")

        instructions = Label(fenetre, text="\nEntrer les critères de recherche\n", font="FreeSerif 14 bold").grid(row=0,
                                                                                                                  column=1)

        lab = Label(fenetre, text="Noms et prénoms d'auteurs présents dans la galaxie :", font="Arial 11").grid(
            sticky="w", row=1, column=1)
        auteur = Entry(fenetre, width=100)
        auteur.grid(row=1, column=2)

        lab2 = Label(fenetre, text="Noms et prénoms d'auteurs absents de la galaxie :", font="Arial 11").grid(
            sticky="w", row=2, column=1)
        notauteur = Entry(fenetre, width=100)
        notauteur.grid(row=2, column=2)

        lab3 = Label(fenetre, text="Date de publication :\n(Donner un intervalle)", font="Arial 11").grid(sticky="w",
                                                                                                          row=3,
                                                                                                          column=1)
        date = Entry(fenetre, width=80)
        date.insert(0, '[ AAAA - AAAA ]')
        date.grid(sticky="w", row=3, column=2)

        lab4 = Label(fenetre, text="Mots présents dans le titre :", font="Arial 11").grid(sticky="w", row=4, column=1)
        mcles = Entry(fenetre, width=100)
        mcles.grid(row=4, column=2)

        lab5 = Label(fenetre, text="Mots absents des titres :", font="Arial 11").grid(sticky="w", row=5, column=1)
        notmcles = Entry(fenetre, width=100)
        notmcles.grid(row=5, column=2)

        lab6 = Label(fenetre, text="Longueur minimale du texte :", font="Arial 11").grid(sticky="w", row=6, column=1)
        empan = Entry(fenetre, width=30)
        empan.grid(sticky="w", row=6, column=2)

        lab7 = Label(fenetre, text="Longueur minimale du plus long texte de la galaxie :", font="Arial 11").grid(
            sticky="w", row=7, column=1)
        ltexte_max = Entry(fenetre, width=30)
        ltexte_max.grid(sticky="w", row=7, column=2)

        lab8 = Label(fenetre, text="Nombre minimal de noeuds dans la galaxie :", font="Arial 11").grid(sticky="w",
                                                                                                       row=8, column=1)
        nbnoeuds_min = Entry(fenetre, width=30)
        nbnoeuds_min.grid(sticky="w", row=8, column=2)

        requete = dict()

        space = Label(fenetre, text="\n").grid(row=10)
        bouton = Button(fenetre, text="Valider", command=recupere).grid(row=11, column=2)
        close = Button(fenetre, text="Fermer", command=fenetre.quit).grid(sticky="w", row=11, column=1)
        fenetre.bind("<Return>", lambda e: recupere())
        fenetre.bind("<Escape>", lambda e: fenetre.quit())

        fenetre.mainloop()

        dict_requetes[i] = requete
        i = i + 1

    return dict_requetes


def affichageTotal(nbGraphes):
    root = Tk()
    root.withdraw()
    res = askyesno('Affichage des galaxies', 'Il y a ' + str(nbGraphes) + ' graphes. Voulez-vous les afficher tous ?')
    root.destroy()
    return res

def selectionAffichage():
    def recupListe():
        tmp = listeSelect.curselection()
        for i in tmp:
            res.append(listeSelect.get(i))
        fenetre.destroy()

    graphes = os.listdir(parametres.DirGlobal + 'jsons')
    nbGraphes = len(graphes)
    height = 30
    if nbGraphes < height:
        height = nbGraphes
    res = []

    ans = affichageTotal(nbGraphes)
    if ans:
        for i in graphes:
            javaVisualisation.affichage(i)
    else:
        fenetre = Tk()
        fenetre.title("Choix des graphes à visualiser")
        # fenetre.geometry("500x850")
        fenetre.minsize(500, 450)
        fenetre.maxsize(500, 850)

        instructions = Label(fenetre, text="\nSélectionner les graphes à visualiser\n", font="Times 14 bold")
        instructions.pack()

        scrollbar = Scrollbar(fenetre, orient='vertical')
        listeSelect = Listbox(fenetre, font="Times", width=50, height=height, yscrollcommand=scrollbar.set,
                              selectmode='multiple')
        scrollbar.config(command=listeSelect.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')

        for i in graphes:
            tab = [int(s) for s in re.findall(r'\d+', i)]
            if len(tab) == 1:
                texte = "Galaxie numéro " + str(tab[0]) + " contenant " + str(len(dirGalaxies[str(tab[0])])) + " noeuds"
            elif len(tab) == 2:
                dirAmas = shelve.open(parametres.DirBD + '/listeAmasGalaxie' + str(tab[0]))
                texte = "Amas numéro " + str(tab[1]) + " de la galaxie " + str(tab[0]) + " contenant " + str(
                    len(dirAmas[str(tab[1])])) + " noeuds"
                dirAmas.close()
            else:
                print('erreur : ' + i)
                print(tab)
            listeSelect.insert(END, texte)

        dirGalaxies.close()

        listeSelect.pack()
        bouton = Button(fenetre, text="Valider", command=recupListe).pack()
        space = Label(fenetre, text="\n").pack()
        fenetre.mainloop()

    return res

# def selectionAffichage():
#     def recupListe():
#         tmp = listeSelect.curselection()
#         for i in tmp:
#             res.append(listeSelect.get(i))
#         fenetre.destroy()
#
#     graphes = os.listdir(parametres.DirGlobal + 'jsons')
#     nbGraphes = len(graphes)
#     height = 30
#     if nbGraphes < height:
#         height = nbGraphes
#     res = []
#
#     ans = affichageTotal(nbGraphes)
#     if ans:
#         for i in graphes:
#             javaVisualisation.affichage(i)
#     else:
#         fenetre = Tk()
#         fenetre.title("Choix des graphes à visualiser")
#         # fenetre.geometry("500x850")
#         fenetre.minsize(500, 450)
#         fenetre.maxsize(500, 850)
#
#         instructions = Label(fenetre, text="\nSélectionner les graphes à visualiser\n", font="Times 14 bold")
#         instructions.pack()
#
#         scrollbar = Scrollbar(fenetre, orient='vertical')
#         listeSelect = Listbox(fenetre, font="Times", width=50, height=height, yscrollcommand=scrollbar.set,
#                               selectmode='multiple')
#         scrollbar.config(command=listeSelect.yview)
#         scrollbar.pack(side=RIGHT, fill=Y)
#
#         dirGalaxies = shelve.open(parametres.DirBD + '/listeGalaxies')
#
#         for i in graphes:
#             tab = [int(s) for s in re.findall(r'\d+', i)]
#             if len(tab) == 1:
#                 texte = "Galaxie numéro " + str(tab[0]) + " contenant " + str(len(dirGalaxies[str(tab[0])])) + " noeuds"
#             elif len(tab) == 2:
#                 dirAmas = shelve.open(parametres.DirBD + '/listeAmasGalaxie' + str(tab[0]))
#                 texte = "Amas numéro " + str(tab[1]) + " de la galaxie " + str(tab[0]) + " contenant " + str(
#                     len(dirAmas[str(tab[1])])) + " noeuds"
#                 dirAmas.close()
#             else:
#                 print('erreur : ' + i)
#                 print(tab)
#             listeSelect.insert(END, texte)
#
#         dirGalaxies.close()
#
#         listeSelect.pack()
#         bouton = Button(fenetre, text="Valider", command=recupListe).pack()
#         space = Label(fenetre, text="\n").pack()
#         fenetre.mainloop()
#
#     return res
