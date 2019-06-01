import lecture_fic


class Score:

    file_to_lang = {'FR': 'ressource/french_lemmas.txt'}

    def __init__(self, lang='FR'):
        self.lang = lang
        self.lemmatizer = self.build_lemmatizer()

    def build_lemmatizer(self):
        return lecture_fic.parse_lemmas(self.file_to_lang[self.lang])

