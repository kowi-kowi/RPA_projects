import re
import pickle

grups = {
    'sv':'464372410f16f100c8d729a703050e49',
    'de':'724e61934f982e00be4b24d18110c7b8',
}
class ReturnToDeSe:

    def __init__(self, text):
        self.description = text


    def langDetect(self,text):
        text = [text]
        print()
        print(text)
        f = open('langClf.pickle', 'rb')
        clf = pickle.load(f)
        f.close()
        lang = clf.predict(text)
        return lang[0]

    def decide(self):

        gr = ''
        text = str(self.description)
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        tab = re.findall("[A-Z].*?[\.!?]", text, re.MULTILINE | re.DOTALL)

        if tab:
            if len(tab) > 2:
                text = tab[0] + ' ' + tab[1]
            else:
                text = ' '.join(tab)

        try:

            lang = self.langDetect(text)
            print(lang)


            if lang == 'sv':
                gr = grups['sv']
            elif lang == 'de':
                gr = grups['de']
        except:
            gr = ''

        if gr:
            return {'u_assignment_group':gr}
        else:
            return gr