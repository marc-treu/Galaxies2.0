import baseDonnees
import lecture_fic

import math
import sqlite3


class Score:

    file_to_lang = {'FR': ['ressource/french_lemmas.txt', 'ressource/french_lexicon.txt']}

    def __init__(self, project_path, lang='FR'):
        self.lang = lang
        self.project_path = project_path
        self.lemmatizer = None
        self.lexicon = None
        self.sum_occurence = 1
        self.build_probabilities()

    def build_lemmatizer(self):
        return lecture_fic.parse_lemma(self.file_to_lang[self.lang][0])

    def build_probabilities(self):
        lexicon, sum_occurence = lecture_fic.parse_lexicon(self.file_to_lang[self.lang][1])
        self.sum_occurence = sum_occurence
        self.lexicon = lexicon
        baseDonnees.fill_score(self.project_path, lexicon)

    def compute_score(self):
        self.lemmatizer = self.build_lemmatizer()
        connexion = sqlite3.connect(self.project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
        cursor_galaxies = connexion.cursor()
        cursor_node = connexion.cursor()
        cursor = connexion.cursor()

        cursor_galaxies.execute('''SELECT idGalaxie FROM degreGalaxies''')
        galaxy_id = cursor_galaxies.fetchone()

        while galaxy_id:
            cursor_node.execute('''SELECT idNoeud, texte FROM texteNoeuds WHERE idGalaxie = (?)''', galaxy_id)
            list_info = cursor_node.fetchall()
            list_nodes = [node[0] for node in list_info]

            score = self.get_score_galaxy(list_nodes, list_info, cursor)
            cursor.execute('''UPDATE degreGalaxies SET score = (?) WHERE idGalaxie = (?)''', (score, galaxy_id[0],))
            galaxy_id = cursor_galaxies.fetchone()

        connexion.commit()
        connexion.close()

    def get_score_galaxy(self, list_nodes, list_info, cursor):

        set_nodes = dict()
        for node in range(len(list_info)):
            set_nodes[list_info[node][0]] = node
            list_info[node] = self.lemmatizer_text(list_info[node][1])

        score = 0

        for node in range(len(list_info)):
            cursor.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (list_nodes[node],))
            node_son = [int(i[0]) for i in cursor.fetchall() if int(i[0]) in set_nodes]
            for id_son in node_son:
                score += self.compute_score_node(list_info[node], list_info[set_nodes[id_son]], cursor)
            del set_nodes[list_nodes[node]]
        return score / len(list_nodes) if score > 0 else 0

    def lemmatizer_text(self, text):
        return [self.lemmatizer.get(word, word) for word in text.split()]

    def compute_score_node(self, list_lems_1, list_lems_2, cursor):

        score = 0

        for lem in set(list_lems_1).intersection(list_lems_2):
            score += math.log(self.sum_occurence / self.lexicon.get(lem, 1))
        #  return 1
        return score