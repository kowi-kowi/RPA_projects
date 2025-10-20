from BasicSNC import BasicSNC
from StaticRules import StaticRules
from ReturnToDeSe import ReturnToDeSe
from SpamChecker import SpamChecker
import conf
from time import sleep
from Decision1 import Decision
from Logs import Logs
from time import sleep
from datetime import datetime

if __name__ == '__main__':

 
 
    mainObject = BasicSNC(conf.usr, conf.pas, conf.HOST)


    logi = Logs()

           'call_type=email^u_assignment_groupSTARTSWITHOC CS FI^ORu_assignment_groupSTARTSWITHBilling FI&sysparm_limit=10')

    while True:

        #dodatek na potrzeby tego tygodnia
        t = datetime.today()
        if (t.hour>17 or t.hour<7):
            print('...')
            sleep(200)
            continue

        #1 pobierz namiary tixów , to w kolejce u CS'ów
        tixy_u_CSFI =mainObject.queue('new_call','call_type=email^u_assignment_groupSTARTSWITHOC CS FI^ORu_assignment_groupSTARTSWITHBilling FI&sysparm_limit=10')
        #2 sprawdź logi, czy już to było ruszane
        print(tixy_u_CSFI)
        #jak tak, pomiń, jak nie, przeslij do kolejki robota
        for element in tixy_u_CSFI:

            fp = open('tmp_log.txt','r')
            l = fp.read()
            fp.close()
            if element in l:
                print('TU TU TU JESTEM')
                continue
            else:
                fp = open('tmp_log.txt','a+')
                c = mainObject.getCallDetails(element)
                print(c['number'])
                fp.write(str(element)+'=>'+c['number']+'\n')
                fp.close()
                dane= {'u_assignment_group':'16a7e2b60f88de402b58716ce1050e53'}
                mainObject.updateCall(element,dane)


        ##koniec dodatku

        #to do:
        #podpiac spam
        #przetrenować modele
        sleep(10)
        calls = mainObject.queue('new_call','call_type=email^u_assignment_group=16a7e2b60f88de402b58716ce1050e53')

        for element in calls:
            #main loop
            caller = ''
            sh_desc = ''
            desc = ''
            number = ''


            call = mainObject.getCallDetails(element)

#zmienne lokalne caller, sh_desc, desc
            caller = call['caller']
            sh_desc = call['short_description']
            desc = call['description']
            number = call['number']
            company = call['company']
            print(caller,' ', sh_desc, ' ', desc)
        #
        #call_object = CaseText(caller,sh_desc,desc)
        #spam check
            #SPAMRule = SpamChecker(caller,'nan','nan').spamData()

            #if SPAMRule:
             #   mainObject.updateCall(element, SPAMRule)
              #  logi.addLog(number + ': SPAM')

        #rule statyczne
            SRules = StaticRules(caller,sh_desc,desc,company).decision()


            if SRules:
                mainObject.updateCall(element, SRules)

                callType = SRules.get('call_type','')

                if callType == 'Incident' or callType == 'Request':

                    call = mainObject.getLink(element)
                    url = call['link']

                    data = {"assignment_group":SRules.get('u_assignment_group'),"u_owner":SRules.get('u_assignment_group')}
                    print(data)
                    sleep(3)
                    mainObject.sncput(url,data)
                    mainObject.sncput(url,data)
                    logi.addLog(number+': Static rule')
                #tutaj dodac przypisywanie wyniku do odpowiedniej kolejki
                continue

        #rozpoznawanie jezyka
            giveToSeDe = ReturnToDeSe(desc).decide()
            if giveToSeDe:
                mainObject.updateCall(element, giveToSeDe)
                logi.addLog(number + ': DE or SE language')
                continue

        #decyzja czy request czy incydent
        #decyzja na temat SO

            Typ = {}


            Typ = Decision(sh_desc,desc).mainDecision()

            if Typ:
                print(Typ)

                ##dodatek na czas testów
                if '0ef71052dbb6670447ff303c7c9619e2' in str(Typ):
                    #oddaj do CS
                    dane = {'u_assignment_group': '90ea8cb50f663100c8d729a703050eff'}
                    mainObject.updateCall(element, dane)
                else:

                    logi.addLog(number + ': Decision:' + str(Typ))
                    mainObject.updateCall(element, Typ)
                    call = mainObject.getLink(element)
                    url = call['link']
                    data = {"assignment_group": Typ.get('u_assignment_group'), "u_owner": Typ.get('u_assignment_group')}
                    mainObject.sncput(url, data)
                    sleep(5)
                    mainObject.sncput(url, data)
