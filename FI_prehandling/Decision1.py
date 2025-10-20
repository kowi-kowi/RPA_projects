from langdetect import detect
import re
import pickle
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from nltk import word_tokenize
from string import punctuation

SO = {
    'other':'0ef71052dbb6670447ff303c7c9619e2',
    'sending':'4ef71052dbb6670447ff303c7c9619d9',
    'receiving':'02f71052dbb6670447ff303c7c9619d6',
    'edi':'f5f71052dbb6670447ff303c7c9619a6',
    'ipost':'86f71052dbb6670447ff303c7c9619e5',
}

class Decision:
    def __init__(self,sh_desc,desc):
        self.sh_desc = sh_desc
        self.desc = desc


    def clenDesc(self,text):
        text = text
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        tab = re.findall("[A-Z].*?[\.!?]", text, re.MULTILINE | re.DOTALL)
        if tab:
            if len(tab) > 4:
                text = tab[0] + ' ' + tab[1] + ' ' + tab[2]
            else:
                text = ' '.join(tab)

        return text

    def finalClean(self,text):
        text = str(text)
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        lang = ''
        language = 'english'
        try:
            lang = detect(text)
        except:
            language = 'english'

        if lang == 'fi':
            language = 'finnish'

        stemmer = SnowballStemmer(language)
        stems = [stemmer.stem(word.lower()) for word in nltk.word_tokenize(text)]
        stems = [word for word in stems if word.isalpha()]
        stems = [word for word in stems if word not in set(stopwords.words(language))]
        stems = [word for word in stems if word not in set(punctuation)]

        return ' '.join(stems)

    def document_features(self,document):
        document_words = set(document)
        features = {}

        f = open('sh_words.pickle', 'rb')
        word_features = pickle.load(f)
        f.close()

        for word in word_features:
            features['contain({})'.format(word)] = (word in document_words)
        return features

    def document_featuresSO(self,document):
        document_words = set(document)
        features = {}

        f = open('so_words.pickle', 'rb')
        word_features = pickle.load(f)
        f.close()

        for word in word_features:
            features['contain({})'.format(word)] = (word in document_words)
        return features

    def decideShDesc(self):
        text = self.sh_desc
        text = self.finalClean(text)

        tab = text.split(' ')
        featur = self.document_features(tab)

        f = open('shDesc.pickle', 'rb')
        clf = pickle.load(f)
        f.close()

        return clf.classify(featur)

    def decideSO(self):

        text1 = self.sh_desc
        text1 = self.finalClean(text1)
        text2 = self.desc
        text2 = self.clenDesc(text2)
        text2 = self.finalClean(text2)
        text = text1 + ' ' + text2
        tab = text.split(' ')

        featur = self.document_featuresSO(tab)

        f = open('service.pickle', 'rb')
        clf = pickle.load(f)
        f.close()

        return clf.classify(featur)

    def document_features2(self,document):
        document_words = set(document)
        features = {}

        f = open('decision2_words.pickle', 'rb')
        word_features = pickle.load(f)
        f.close()

        for word in word_features:
            features['contain({})'.format(word)] = (word in document_words)
        return features

    def decision2(self):
        text1 = self.sh_desc
        text1 = self.finalClean(text1)
        text2 = self.desc
        text2 = self.clenDesc(text2)
        text2 = self.finalClean(text2)
        text = text1 + ' ' + text2
        tab = text.split(' ')

        featur = self.document_features2(tab)

        f = open('decision2_clf.pickle', 'rb')
        clf = pickle.load(f)
        f.close()

        return clf.classify(featur)

    def decision3(self):

        lang = 'en'
        try:
            lang = detect(self.clenDesc(self.desc))
        except:
            lang = 'en'
        text1 = self.sh_desc
        text1 = self.finalClean(text1)
        text2 = self.desc
        text2 = self.clenDesc(text2)
        text2 = self.finalClean(text2)
        text = text1 + ' ' + text2
        tab = text.split(' ')

        f = open('FImodel.pickle', 'rb')
        clf_fi = pickle.load(f)
        f.close()

        f = open('ENmodel.pickle', 'rb')
        clf_en = pickle.load(f)
        f.close()

        if lang == 'fi':
            wynik = clf_fi.predict(tab)
        else:
            wynik = clf_en.predict(tab)

        inc = 0
        req = 0

        for element in wynik:
            if 'inc' in elemen.lower():
                inc = inc + 1
            else:
                req = req + 1

        if inc > req :
            return 'Incident'
        else:
            return 'Request'

    def statucRulesForSO(self):
        text = self.sh_desc + ' ' + self.desc

        send = ['reititys/reitittää','poista lasku', 'poistakaa lasku','remove the invoice', 'bels']
        ipost = ['palkkalaskelma', 'payslip', 'omaposti']
        edi = ['desadv', 'edi', 'orders', 'sanoma', 'sanomat']
        receiving = ['sähköpostilasku', 'email', 'invoice']

        for element in edi:
            if element in text.lower():
                return 'edi'

        for element in receiving:
            if element in text.lower():
                return 'receiving'

        for element in send:
            if element in text.lower():
                return 'sending'

        for element in send:
            if element in text.lower():
                return 'ipost'

        return 'empty'


    def mainDecision(self):

        inc = 0
        req = 0

        typ = ''

        so = self.statucRulesForSO()
        try:
            if so == 'empty':
                so = self.decideSO()
        except:
            so = 'other'
        try:
            decision1 = self.decideShDesc()
        except:
            decision1 = 'inc'

        try:
            decision2 = self.decision2()
        except:
            decision2 = 'inc'
        try:
            decision3 = self.decision3()
        except:
            decision3 = 'inc'

        if 'inc' in decision1.lower():
            inc = inc + 1
        else:
            req = req + 1

        if 'inc' in decision2.lower():
            inc = inc + 1
        else:
            req = req + 1

        if 'inc' in decision3.lower():
            inc = inc + 1
        else:
            req = req + 1

        if inc > req:
            typ = 'Incident'
        else:
            typ='Request'

        print('typ=',typ)
        print('SO=',so)

        if typ == 'Incident':
            return {"call_type":"Incident","u_service":SO[so],"u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        else:
            return {"call_type": "Request", "u_service": SO[so],
                        "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Support Request",
                        "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}


