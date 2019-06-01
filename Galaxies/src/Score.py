import baseDonnees
import lecture_fic

import sqlite3


class Score:

    file_to_lang = {'FR': ['ressource/french_lemmas.txt', 'ressource/french_lexicon.txt']}

    def __init__(self, project_path, lang='FR'):
        self.lang = lang
        self.project_path = project_path
        self.lemmatizer = self.build_lemmatizer()
        self.build_probabilities()
        self.max_proba = 1

    def build_lemmatizer(self):
        return lecture_fic.parse_lemma(self.file_to_lang[self.lang][0])

    def build_probabilities(self):
        lexicon, sum_occurence = lecture_fic.parse_lexicon(self.file_to_lang[self.lang][1])
        self.max_proba = 1 / sum_occurence
        baseDonnees.fill_score(self.project_path, lexicon, sum_occurence)

    def compute_score(self):
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
        return len(list_nodes)

        # for Noeud in ListeNoeuds:
        #     curseur.execute('''SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?)''', (Noeud,))
