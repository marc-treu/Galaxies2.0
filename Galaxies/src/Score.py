import lecture_fic
import baseDonnees


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

