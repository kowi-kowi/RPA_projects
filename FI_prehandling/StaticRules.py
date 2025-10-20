import re
import pickle
from langdetect import detect
from vats1 import vat

assignmentGroups = {
    'CSFI':'90ea8cb50f663100c8d729a703050eff',
    'CSGLOB':'a0eaccb50f663100c8d729a703050e10',
    'Billing':'9d27bd7537281f4010e81d8643990e4a',
    'ChangeCord':'d943bc2cdb11634004cb948adb9619e5',
}
SO = {
    'other':'0ef71052dbb6670447ff303c7c9619e2',
    'sending':'4ef71052dbb6670447ff303c7c9619d9',
    'receiv':'02f71052dbb6670447ff303c7c9619d6',
    'edi':'f5f71052dbb6670447ff303c7c9619a6',
    'ipost':'86f71052dbb6670447ff303c7c9619e5',

}

class StaticRules:

    def __init__(self , caller, sh_desc, desc,company):

        self.caller = caller.lower()
        self.sh_desc = sh_desc.lower()
        self.desc = desc
        self.company = company


    def langDetect(self,text):
        text = [text]
        print()
        print(text)
        f = open('langClf.pickle', 'rb')
        clf = pickle.load(f)
        f.close()
        lang = clf.predict(text)
        return lang[0]

    def group(self):
        gr = ''
        text = str(self.desc)
        text = text.replace('\n',' ')
        text = text.replace('\r', ' ')
        tab = re.findall("[A-Z].*?[\.!?]", text, re.MULTILINE | re.DOTALL)
        print(tab)
        if tab:
            if len(tab)>2:
                text = tab[0] + ' ' + tab[1]
            else:
                text = ' '.join(tab)

        try:

            print(text)
            lang = self.langDetect(text)

            print(lang, '------------------------------------')

            if lang =='fi':
                gr = assignmentGroups['CSFI']
            else:
                gr = assignmentGroups['CSGLOB']
        except:
            gr = assignmentGroups['CSFI']

        return gr

    def getVat(self, text):

        tunus = re.compile(r'Y-Tunnus:.*?,')
        tmp = tunus.findall(text)

        if tmp:
            t = tmp[0]
            t1 = t.replace('Y-Tunnus: ', '')
            t2 = t1.replace(',', '')
            t3 = t2.replace('-', '')
            t = t3
            return 'FI' + t
        else:
            return ''

    def checkMeseVat(self, text):
        tmpVat = self.getVat(text)

        if tmpVat in vat:
            return True
        else:
            return False
    def ifGeneralInquiry(self,text):
        sh_description_context = ['separate remittance advice',
             'kerro mielipiteesi asioinnistasi postin kanssa',
             'payment advice from',
             'your request fina',
             'payment specification',
             'automaattinen vastaus',
             'Automatic reply',
             'Olemme vastaanottaneet palvelupyyntönne',
             'Your case has been registered',
             'Saimme yhteydenottosi',
             'OCRITM - approve normal user',
             'Reminder for awaiting approvals on OpusCapita Customer Service Portal',
            'news from',
                                  ]

        for element in sh_description_context:
            if element in text:
                return True
        if 'Your Case' in text and 'has been resolved' in text:
            return True
        return False
#--------------------------------------####Main function in this class ######------------
    def decision(self):

        #siple rules
        if self.ifGeneralInquiry(self.sh_desc):

            return {"call_type": "General Inquiry", "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}

        elif 'kesko@service-now.com' in self.caller and ('E-arkisto'.lower() in self.sh_desc or 'eArkisto'.lower() in self.sh_desc + ' ' + self.desc.lower() or 'eArchive'.lower() in self.sh_desc + ' ' + self.desc.lower()):
            return {"call_type": "Transferred to MESE", "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        elif 'din henvendelse er mottatt. vi vil gi deg tilbakemelding' in self.desc.lower() or 'inexchange network, tiedustelun on hyv' in self.desc.lower():
            return {"call_type": "General Inquiry", "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}

        #incident

        elif 'OpusCapita inChannel'.lower() in self.sh_desc:
            return {"call_type": "Incident", "u_service": SO['receiv'],
                    "u_assignment_group": self.group()}
        elif 'Missing acknowledgements on Maventa invoices'.lower() in self.sh_desc:
            return {"call_type": "Incident", "u_service": SO['receiv'],
                    "u_assignment_group": assignmentGroups['CSFI']}
        elif 'SKANNAUS'.lower() in self.sh_desc:

            return {"call_type": "Incident","u_service": SO['receiv'], "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}

        elif 'Missing acknowledgements on Maventa invoices'.lower() in self.sh_desc:

            return {"call_type": "Incident","u_service": SO['receiv'], "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}

        elif 'POSTI MESSAGING ERROR REPORT'.lower() in self.sh_desc or 'Invalid messages report'.lower() in self.sh_desc:

            return {"call_type": "Incident","u_service": SO['sending'],"contact_type":"integration" ,"u_assignment_group": self.group()}

        elif 'Error report from Posti Messaging MCI'.lower() in self.sh_desc:

            return {"call_type": "Incident","u_service": SO['sending'], "contact_type":"integration", "u_assignment_group": self.group()}

        elif 'Virheellinen sanoma Tullille'.lower() in self.sh_desc:
            return{"call_type": "Incident", "u_service": SO['edi'], "u_assignment_group": assignmentGroups['CSFI'] }

        elif ('sirius' in self.caller) or ('stage_emea_emailreceivedigi_01' in self.caller) or ( 'p-l-nagios-1.ocnet.local' in self.caller):
            return {"call_type": "Incident", "u_service": "0ef71052dbb6670447ff303c7c9619e2", "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}

        elif 'Billexco'.lower() in self.sh_desc + ' ' + self.desc:
            return {"call_type": "Incident", "u_service": SO['other'],
                    "u_assignment_group": 'a927bd7537281f4010e81d8643990e58'}

        #return call
        elif 'Do you know this new user?'.lower() in self.sh_desc or 'Reminder for awaiting approvals on OpusCapita Customer Service Portal'.lower() in self.sh_desc:
            return {"u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        elif 'messaging.fi@posti.com' in self.caller and ('pmin' in self.sh_desc or 'pmritm' in self.sh_desc):
            return {"u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        elif 'has been resolved' in self.desc or 'nner du till denna anv' in self.desc:
            return {"u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}

        elif 'Your request  FINA'.lower() in self.sh_desc:
            return {"u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        elif 'kundservice@procountor.com' in self.caller:
            return {"u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        elif self.company == '':
            return {"u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}

        #requests

        elif  'messaging.fi@posti.com' in self.caller and 'LVISNet Extra: Laskutusosoitteen muutos'.lower() in self.sh_desc: #'messaging.fi@posti.com' in self.caller and wyciete do tstow
            return {"call_type": "Request", "u_service": "0ef71052dbb6670447ff303c7c9619e2",
                    "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Customer information change","contact_type":"integration",
                    "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        elif 'monthly report' in self.sh_desc :
            return {"call_type": "Request", "u_service": SO['other'],
                    "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Invoice related Request",
                    "u_assignment_group": assignmentGroups['Billing']}
        
        elif 'service maintenance' in self.desc.lower() or 'maintenance' in self.desc.lower() or 'notification' in self.sh_desc.lower():
            return {"call_type": "Request", "u_service": SO['other'],
                    "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Invoice related Request",
                    "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        
        elif 'LVISNet Extra: Kuukausiraportti'.lower() in self.sh_desc:
            return {"call_type": "Request", "u_service": "0ef71052dbb6670447ff303c7c9619e2",
                    "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Invoice related Request",
                    "u_assignment_group": assignmentGroups['Billing']}

        elif 'LVISNet'.lower() in self.sh_desc + ' ' + self.desc:
            return {"call_type": "Request", "u_service": "02f71052dbb6670447ff303c7c9619f1",
                "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Support Request",
                "u_assignment_group": assignmentGroups['CSFI']}

        elif 'Muutostyöpyyntö, Hakunilan Huolto Oy'.lower() in self.sh_desc:
            return {"call_type": "Request", "u_service": SO['receiv'],
                    "request_item": "e6d119d1b50fa100a3fe2d5895880487", "u_sr_category": "Support Request",
                    "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        elif 'Please maintain email distribution list'.lower() in self.sh_desc:
            return {"call_type": "Request", "u_service": SO['receiv'],
                    "request_item": "e6d119d1b50fa100a3fe2d5895880487", "u_sr_category": "Support Request",
                    "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        elif 'Irtisanotun skannauspalvelun laskujen toimitus'.lower() in self.sh_desc:
            return {"call_type": "Request", "u_service": SO['receiv'],
                    "request_item": "e6d119d1b50fa100a3fe2d5895880487", "u_sr_category": "Support Request",
                    "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
        elif 'Delivery of invoices for cancelled scanning service'.lower() in self.sh_desc:
            return {"call_type": "Request", "u_service": SO['receiv'],
                    "request_item": "e6d119d1b50fa100a3fe2d5895880487", "u_sr_category": "Support Request",
                    "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
            

        elif 'Rautakesko Role Order'.lower() in self.sh_desc:
            return {"call_type": "Request", "u_service": SO['receiv'],
                    "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Customer Order",
                    "u_assignment_group": "d943bc2cdb11634004cb948adb9619e5"}#bo slawek ma problem 06.05.2021"0d277d7537281f4010e81d8643990efe"}

        elif 'Lasku'.lower() in self.sh_desc and '340'.lower() in self.sh_desc:
            return {"call_type": "Request", "u_service": SO['other'],
                    "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Invoice related Request",
                    "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}

        elif 'New virtual connection || talenom ||'.lower() in self.sh_desc:
            return {"call_type": "Request", "u_service": SO['other'],
                    "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Invoice related Request",
                    "u_assignment_group": assignmentGroups['Billing']}
        elif 'OCI '.lower() in self.sh_desc + ' ' +self.desc or 'OpusCapita Invoice'.lower() in self.sh_desc + ' ' +self.desc:
            return {"call_type": "Request", "request_item": "5a697167d9155100527f8082167466cd","u_service": '92f75052dbb6670447ff303c7c961906', "u_sr_category": "Support Request",
                    "u_assignment_group": 'ed27bd7537281f4010e81d8643990e63'}
        elif 'IPA '.lower() in self.sh_desc + ' ' + self.desc:
            return {"call_type": "Request", "request_item": "5a697167d9155100527f8082167466cd","u_service": 'b5018aacdb00ff002660980adb961973',
                    "u_sr_category": "Support Request",
                    "u_assignment_group": 'ed27bd7537281f4010e81d8643990e63'}
        elif 'Kesko Profix store addition'.lower() in self.sh_desc:
            return {"call_type": "Request", "request_item":"5a697167d9155100527f8082167466cd","u_service":  SO['receiv'],"u_sr_category": "Customer Order",
                    "u_assignment_group": assignmentGroups['ChangeCord']}
        
        elif 'Kesko Raksa store addition'.lower() in self.sh_desc:
            return {"call_type": "Request", "request_item":"5a697167d9155100527f8082167466cd","u_service":  SO['receiv'],"u_sr_category": "Customer Order",
                    "u_assignment_group": assignmentGroups['ChangeCord']}
        elif 'Important information about your invoices storage'.lower() in self.sh_desc:
            return {"call_type": "Request", "request_item":"5a697167d9155100527f8082167466cd","u_service":  SO['other'],"u_sr_category": "Support Request",
                    "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}





        #very complicated rules

        if 'postiluotto@intrum.com '.lower() in self.caller: #postiluotto@intrum.com zmien po testach
            if self.checkMeseVat(self.desc):
                return {"call_type": "Transferred to MESE"}  # move to mese data
            elif 'Nimi muuttunut'.lower() in self.sh_desc or 'Saneeraus'.lower() in self.sh_desc:
                return {"call_type": "Request", "u_service": "0ef71052dbb6670447ff303c7c9619e2",
                        "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Support Request",
                        "u_assignment_group": "90ea8cb50f663100c8d729a703050eff"}
            else:
                return {"call_type": "Request", "u_service": "0ef71052dbb6670447ff303c7c9619e2",
                        "request_item": "5a697167d9155100527f8082167466cd", "u_sr_category": "Support Request",
                        "u_assignment_group": assignmentGroups['Billing']}

        #default statement
        else:
            return ''


