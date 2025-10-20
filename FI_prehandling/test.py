from Decision1 import Decision

from SpamChecker import SpamChecker

o = Decision('Itella Worflow laskuja kierrossa ->selvitys Lähettämäsi sähköposti ei ole tavoittanut', ' ')

o.decideShDesc()
print(o.mainDecision())


mail = SpamChecker('ala@1.12345-a-l-a-.com','text','aa')
print('is spam',mail.isSPAM)