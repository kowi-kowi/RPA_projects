from spamData import spam_blackList, endings, keyWords


# zapamiêtac, jak bêde dodawaæ: adres e-mail w czystej postaci przekazywaæ
# listê atachmentów, w postaci tablicy ? zdecydowaæ
# s³owa klucze wyci¹gn¹æ, i dodaæ do pliku, a tu dodaæ funkcje obrabiania tekstu, tak¹ jak do s³ów kluczy


class Reg:
    # to do ###########################

    def checkAttachments(att):
        return False



    def checkKeyWords(text):

        return False

    #####################################33

    def checkBlackList(caller):
        start = caller.index('@')
        tmp = caller[start:-1]

        firstLetter = tmp[1].lower()

        if firstLetter.isdigit():
            firstLetter = 'a'

        if tmp in spam_blackList.get(firstLetter):
            return True
        else:
            return False

    def checkDigits(caller):
        digCounter = 0

        for char in caller:
            if char.isdigit():
                digCounter = digCounter + 1

        if digCounter > 4:
            return True
        else:
            return False

    def checkEndingsAndDots(caller):
        start = caller.index('@')

        tmp = caller[start:]
        print(tmp)
        try:
            t_tmp = tmp.split('.')
            tmp_ending = t_tmp[len(t_tmp) - 1].lower()

            if tmp_ending in endings:
                return True
            else:
                return False
        except:
            if not t_tmp:
                return True

    def checkOtherStuff(caller):
        # no dots after @, 1 letter domain, to many dashes >3
        start = caller.index('@')
        tmp = caller[start:-1]

        # check dashes
        try:
            t_tmp = tmp.split('-')
            if len(t_tmp) > 4:
                return True
        except:
            pass

        t_tmp = tmp.split('.')

        if len(t_tmp[0]) < 3:
            return True
        else:
            return False

    def checkAll(exeFile, onBlackList, toManyDigits, wierdEndings, otherStuff, keyWords):

        if not exeFile and not onBlackList and not toManyDigits and not wierdEndings and not otherStuff and not keyWords:
            return False
        else:
            return True


class SpamChecker(Reg):
    def __init__(self, caller, text, attachments):
        # caller should be check for e-mail properties
        # text key words
        # attachments if exe files
        self.caller = caller
        self.text = text
        self.attachments = attachments
        self.exeFile = Reg.checkAttachments(self.attachments)
        self.onBlackList = Reg.checkBlackList(self.caller)
        self.toManyDigits = Reg.checkDigits(self.caller)
        self.wierdEndings = Reg.checkEndingsAndDots(self.caller)
        self.otherStuff = Reg.checkOtherStuff(self.caller)  # 1 letter domain, to many dashes >3
        self.keyWords = Reg.checkKeyWords(self.text)

        self.isSPAM = Reg.checkAll(self.exeFile, self.onBlackList, self.toManyDigits, self.wierdEndings,
                                   self.otherStuff, self.keyWords)

    def spamData(self):

        if self.isSPAM:
            return {"call_type": "SPAM"}
        else:
            return ''












