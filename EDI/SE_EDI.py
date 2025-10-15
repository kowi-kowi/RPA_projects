import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from time import sleep
import re
import os
import json
import unicodedata
import uuid
from datetime import datetime

import conf
import log



#global variables

HOST = conf.HOST
USR = conf.USR
PWD = conf.PWD

CS_XIB = 'e127bd7537281f4010e81d8643990e86'
CS_XIB='ce62c3d60f6ad6009368f88ce1050ed0'

SE_ROBOT_QUEUE = '894b206cdb5448140ffa9407db9619e1'

companies={

    '020ccd2037d836002e7bd1b543990e2a':'Lexmark',
    'fc070f420fef7100c8d729a703050ee8':'InExchange', #tu trzeba decyzje podjac na podstawie short description
    '452109880f0931000deac453e2050e14':'Basware',
    '7832c5c80f0931000d5eac453e2050ea4':'Pagero',
    '6e3586e737eb4300a2128f0843990e30':'Tieto',
    '8dbb34ee4fa107c02648c0f18110c7b0':'Visma',
    'e1902c610f7d3100c8d729a703050e0a':'CGI', #company inactive
    '58d6b0674f9d7a80be4b24d18110c744':'Scancloud',
    '54ba08754f49be001d1a36e18110c700': 'Crediflow', #09.12.2019 new definition
    'a39ed0920f7b35000deac453e2050e1e': 'Palette', #11.12.2019 new definition

}



def getListOfAttachments(inc):
    
    l=list()
    

    inc_url=HOST+'/api/now/table/sys_attachment?sysparm_query=table_sys_id%3D'+inc
   
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    response = requests.get(inc_url, auth=(USR, PWD), headers=headers )

    proba = 0

    print(str(response.status_code))
    while response.status_code!=200:
        response = requests.get(inc_url, auth=(USR, PWD), headers=headers )
        proba= proba + 1
        print(str(response.status_code)+"powtorka nr:"+str(proba))
        if proba == 5:
            break
        sleep(5)
        
    lista=response.json()['result']

    for element in lista:
        d=dict()
        d.update({'sys_id': element.get('sys_id','')})
        d.update({'file_name':element.get('file_name','')})
        l.append(d)

    

    return l




def goToTmp():

    path = os.getcwd()
    if 'tmp' not in path:
        os.chdir('tmp')

def exitTmp():
    
    path = os.getcwd()
    if 'tmp' in path:
        os.chdir('..')
def cleanTmp():

    print('clean tmp')
    goToTmp()

    listOfFiles= os.listdir()

    for file in listOfFiles:
        os.remove(file)
    
def getAttachments(lista1):
    
    print(lista1) 
    
    goToTmp()

    for element in lista1:
        if element.get('file_name')!='':
            h= {"Content-Type":"application/xml","Accept":"*/*"}
            u=HOST+"/api/now/attachment/"+element.get('sys_id')+"/file"
            r = requests.get(u, auth=(USR, PWD), headers=h )
            filename = element.get('file_name').replace(':','')
            filename = filename.replace('<','')
            filename = filename.replace('>','')
            element['file_name'] = filename
            handle = open(element.get('file_name'), "wb")

            for chunk in r.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    handle.write(chunk)
            handle.close()

    sleep(10)
    exitTmp()

    return lista1
def cutFile(text):
    tmp = str(text).split('\n')
    text = ''
    for i, element in enumerate(tmp):
        if i > 50:
            break

        text = text + element + '\n'

    print(text)
    return text
    
        
def getFilesText(list_of_attachments):
    text = ''
    delimiter =(20 * '%') + '\n'
    goToTmp()
    try:
        for element in list_of_attachments:
            with open(element['file_name'], 'r') as f:
                tmp = f.read()
                if 'xml' in tmp or 'XML' in tmp:
                    tmp = cutFile(tmp)
                    text = text + delimiter + tmp

        
        exitTmp()
        return text
    except:
        return ''



def getDataFromQueue():
    url=HOST+'/api/now/table/incident?sysparm_query=assignment_group%3D'+SE_ROBOT_QUEUE+'%5EstateNOT%20IN6%2C7'
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    response = requests.get(url, auth=(USR,PWD), headers=headers )
    
    if response.status_code != 200: 
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()

    data = response.json()
    co=data['result']

    return co

def returnToCS(sys_id, where,message):
    url = HOST+'/api/now/table/incident/'+sys_id
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    work_notes=message

    

    
    dane = json.dumps({"assignment_group":where,"state":"2","work_notes":work_notes})

    response = requests.put(url, auth=(USR,PWD), headers=headers ,data=dane)

    dane = json.dumps({"work_notes":work_notes})

    if response.status_code != 200: 
        return 'ERROR'



def workInProgress(sys_id):

    url=HOST+'/api/now/table/incident/'+sys_id
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    d=json.dumps({"assigned_to":"a16d9d7b2b9579000bc85ffb27da15ac","state":"-6"})
    response = requests.put(url, auth=(USR,PWD), headers=headers ,data=d)



def closeTicket(sys_id, message):
    url=HOST+'/api/now/table/incident/'+sys_id
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    #d=json.dumps({"close_notes":message,"subcategory":"Routing Error","u_failure_party":"3rd party / customer's vendor","state":"6", "u_disable_notification":"true"})
    d=json.dumps({"close_notes":message,"close_code":"Resolve (repeatable)","state":"6", "u_disable_notification":"true"})
    response = requests.put(url, auth=(USR,PWD), headers=headers ,data=d)
def getLexmark(text):
    try:
        a = text.index('Leverantör:')
        b = text.index('Köpare:')
    except:
        try:
            a = text.index('Supplier:')
            b = text.index('Buyer:')
        except:
            a=1
            b = len(text)
    text = text[a:b]
    

    t = text.split('\n')
    
    name = ''
    Organisationsnr = ''
    Momreg = ''

    for element in t:

        if 'Supplier address Name:' in element:
            name = element.strip(' ')[22:].strip(' ').lower()
            break

        elif 'Namn:' in element or 'Name:' in element:
            name = element.strip(' ')[5:].strip(' ').lower()
            break
        elif 'Organisationsnr:' in element:
            Organisationsnr = element.strip(' ')[25:].strip(' ')
        elif 'Sweden, VAT no:' in element:
            Organisationsnr = element.strip(' ')[14:].strip(' ')
        elif 'Momsreg.nr:' in element:
            Momreg = element.strip(' ')[20:].strip(' ')

    #return Organisationsnr  ##zdecyduj sie na oddanie jednej rzeczy
    if name:
        return name
    else:
        return '***************'

def getInExchange(title,text):

    

    if 'tekniskt fel' in title.lower():
        #pobierz zalacznik i zwroc contakt z zalacznika ------------------------------------tuz mieniam 19 maj 2020

        
        tmp_text = text.replace('\n','')
        
        seller = re.compile(r'SellerParty.*?SellerParty')

        t = seller.findall(tmp_text)

        

        name = re.compile(r':Name.*?:Name')

        try:
            n = name.findall(t[0])
        except:
            return '*********************'

        

        if n:

            return n[0][6:-10]
        else:
            return '*********************'
    else:
        
        keyword = 'Utställare'
        customerName = ''

        table = text.split('\n')
        lista = list()

        for element in table:
            if keyword in element:
                lista.append(element)

        if lista:
            customerName = lista[0][len(keyword):].strip()


        if customerName:
            return customerName
        else:
            return '***************'
    

def getBasware(text): ###return number

    #return customer number
    key_words = ["Sender's ID:","Sender:", "Sender's Name:"]
    #return customer name

    #key_words = ["Sender's Name"]
    
    keyword = "Sender's ID:"
    keyword1 = "Sender: "
    customerNumber = ''
    table = text.split('\n')
    lista = list()

    for element in table:
        if keyword in element:
            lista.append(element)
    if not lista:
        keyword = keyword1
        for element in table:
            if keyword in element:
                lista.append(element)

    if lista:
        customerNumber = lista[0][len(keyword):].strip()

    if customerNumber:
        return ' '+customerNumber+' '
    else:
        return '**********'


def getPagero(short_description, text): ####also attachments to be add

    if short_description == 'Unhandled erroneous documents' and ('You have received a new Pagero message.' in text and 'Medicarrier AB' in text):

        return 'close'

    else:

        keyword = 'Issuer:'
        customerName = ''

        table = text.split('\n')
        lista = list()

        for element in table:
            if keyword in element:
                lista.append(element)

        if lista:
            customerName = lista[0][len(keyword):].strip()

        if customerName:
            return customerName+' '
        else:
            return '****************'

##def getTieto(text):
##    keyword = 'Utställare:'
##    customerName = ''
##
##    table = text.split('\n')
##    lista = list()
##
##    for element in table:
##        if keyword in element:
##            lista.append(element)
##
##    if lista:
##        customerName = lista[0][len(keyword):].strip()
##
##
##    if customerName:
##        return customerName+' '
##    else:
##        return '****************'
######zmiana ze wzgledu OCIN02564787
def getTieto(text):
    keyword = 'Utställare:'
    keyword2 = 'sender:'
    customerName = ''

    table = text.split('\n')
    lista = list()

    for element in table:
        if keyword in element or keyword2 in element:
            lista.append(element)

    if lista:
        if keyword in lista[0]:
            customerName = lista[0][len(keyword):].strip()
        elif keyword2 in lista[0]:
            print('tu jestem')
            tmp = lista[0].split('(')
            print(tmp)
            customerName = tmp[0][len(keyword2):]

    if not customerName :
        #05.10.2020 sprawdzam nowy typ tixów
        tmp = table[0]

        name = re.compile(r'\([0-9]+\)')
        n = name.findall(tmp)
        if n:

            n = n[0]
            n = n.replace('(','')
            n = n.replace(')','')
            
            n = int(n)
        if n:
            customerName = n


    if customerName:
        return str(customerName)+' '
    else:
        return '****************'

def getVisma(text):
    keyword = 'Sender id:'
    customerName = ''

    table = text.split('\n')
    lista = list()

    for element in table:
        if keyword in element:
            lista.append(element)

    if lista:
        customerName = lista[0][len(keyword):].strip()


    if customerName:
        return customerName+' '
    else:
        return '****************'
##zakomentowana funkcja 27.02.2020, funkcja poni¿ej w uzyciu
def getCGI(text):
    
    

    try:
        start = text.index('SellerParty>')
        print(start)
        l = text[start:].split('\n')
        number = ''

        for element in l:
            if '<cac:ID>' in element or '<cac:CompanyID>' in element:
                print(element)
                for n in element:
                    if n.isdigit():
                        number = number + n
                break
                        
        if number:

            return ' '+number+' '

        else:
            return '***********'
        
    except:
        try:
            sup = re.compile(r'<SuppliersContact><Name>(.*)</Name>')
            b = sup.findall(text)
            start = b[0].index(',')
            b[0] = b[0][:start]
            return b[0]
        except:
            return '**********'    
##def getCGI(text):
##    
##    
##
##    try:
##        start = text.index('SellerParty>')
##        l = text[start:].split('\n')
##        number = ''
##
##        for element in l:
##            if '<cac:ID>' in element or '<cac:CompanyID>' in element:
##                print(element)
##                for n in element:
##                    if n.isdigit():
##                        number = number + n
##                break
##                        
##        if number:
##
##            return ' '+number+' '
##
##        else:
##            return '***********'
##        
##    except:
##        return '**********'
##    keyword = 'SellerParty'
##    customerName = ''
##
##    start = text.index(keyword)
##
##    customerName = text[start:]
##    tablica = customerName.split('\n')
##    customerName = tablica[6].strip()
##    start = customerName.index('>')
##    stop = customerName.index('</')
##    return customerName[start + 1:stop].strip()
    
##    try:
##        start = text.index('Sender-id in the SBDH-header: ')
##        text1 = text[start : ]
##        stop = text1.index('\n')
##        text1 = text1[30:stop].replace('SE','')
##        return text1
##        
##    except:
##        try:
##            start = text.index('CompanyID')+10
##            text1 = text[start:]
##            stop = text1.index('<')
##            text1 = text1[:stop]
##            return text1.replace('SE','')
##            
##        except:
##            try:
##                result = re.search('SellerParty(.*)SellerParty', text)
##                wynik = result.group(1)
##
##                l = wynik.split('>')
##
##                lista = list()
##                for i, element in enumerate(l):
##                    if '</cac:CompanyID' in element:
##                        lista.append(element)
##
##                    if i > 37:
##                        break
##                t = lista[0].replace('</cac:CompanyID','')
##                t = t.replace('SE','')
##                t.strip()
##
##                if t:
##                    return ' '+t+' '
##                else:
##                    return '**************'
##            except:
##                return '**********'
##    

def getScancloud(text):
    keyword = 'Seller party:'
    customerName = ''

    table = text.split('\n')
    lista = list()

    for element in table:
        if keyword in element:
            lista.append(element)

    if lista:
        customerName = lista[0][len(keyword):].strip()
        t = customerName.split(',')
        customerName = t[0].strip()

    if customerName:
        return customerName
    else:
        return '****************'

def getCrediflow(text):

    keyword = 'Sender:'
    customerName = ''

    table = text.split('\n')
    lista = list()

    for element in table:
        if keyword in element:
            lista.append(element)

    if lista:
        customerName = lista[0][len(keyword):].strip()
        t = customerName.split(',')
        customerName = t[0].strip()

    if customerName:
        return customerName
    else:
        return '****************'

def getPalette(text):
    
    keyword = 'ndare            : '
    customerName = ''

    table = text.split('\n')
    lista = list()

    for element in table:
        if keyword in element:
            lista.append(element)

    if lista:
        customerName = lista[0][len(keyword):].strip()
        t = customerName.split(':')
        customerName = t[1].strip()

    if customerName:
        return customerName
    else:
        return '****************'
#####funkcja dodana 03/03/2020 z racji na nie dzialajace znaki

def checkChar(text):
    znaki = range(0,300)
    tmp = text
    for znak in text:
        if ord(znak) not in znaki:
            
            index = text.index(znak)
            tmp = text[0:index+2] + text[index+3:]

    text = tmp

    return tmp

def getAddress(who,title,description):

    conntact = ''
    tmp = ''
    companyT = who
    if companyT == 'Lexmark' :
        conntact =  getLexmark(description)
    elif companyT == 'InExchange':
        conntact = getInExchange(title,description)

    elif companyT == 'Basware':
        conntact = getBasware(description)

    elif companyT == 'Pagero':

        conntact = getPagero(title,description)

    elif companyT == 'Tieto':
        conntact = getTieto(description)
    elif companyT == 'Visma':
        conntact = getVisma(description)
    elif companyT == 'CGI':
        conntact = getCGI(description)
    elif companyT == 'Scancloud':
        conntact = getScancloud(description)
    elif companyT=='Crediflow':
        conntact = getCrediflow(description)
    elif companyT=='Palette':
        conntact = getPalette(description)
    print('in ticket has been found conntact: '+conntact)

    if conntact == 'close': ###zamykanie dla Pagero bedzie dzialac dla innych tez
        return 'close'
    else:
        conntact = checkChar(conntact) #######################################03/03/2020
        conntact = conntact.strip()
        conntact = conntact+' ,'
        with open(r'C:\Users\admin_kowalma1.OC\Documents\RPA\SE_EDI\EDI_improvement\EDI_improvement\New folder\kontakty.txt','r') as fp:
            line = fp.readline()
            while line:

                if conntact.lower().strip() in line.lower():
                    
                    tmp = line
                    break
                line = fp.readline()
                
                
        if tmp :
            contact = tmp.split(',')[-1]
            t = contact.split(';')
            

            c = ''
            for element in t:
                if element and 'opuscapita' not in element and '@' in element and '\n' not in element:
                    c = c + element +';'
            
            
            print(c)
            return c #tmp.split(',')[-1]
        else:
            return ''

def send_mail(driver,sys_id, description,who_to_inform ):
    message_start = '''Hej, 
Se nedan felmeddelande om stoppad fil:


'''
    message =  message_start + description

    #url = HOST + '/email_client.do?sysparm_table=incident&sysparm_sys_id='+sys_id+'&sysparm_target=incident&sys_target=incident&sys_uniqueValue='+sys_id+'&sys_row=0&sysparm_encoded_record=&sysparm_domain_restore=false&sysparm_stack=no'

    url = HOST + '/email_client.do?sysparm_table=incident&sysparm_sys_id='+sys_id+'&sysparm_target=incident&sys_target=incident&sys_uniqueValue='+sys_id+'&sys_row=0&sysparm_encoded_record=&sysparm_domain_restore=false&sysparm_stack=no'
    driver.get(url)
    time.sleep(5)
    #/ html / body / div[2] / form / div[1] / div / div / span[1] / span
    try : 
        elem = driver.find_element_by_xpath('/html/body/div[2]/form/div[1]/div/div/span[1]/span')
        elem.click()
        elem.send_keys(Keys.BACKSPACE)
    except:
        pass

    elem = driver.find_element_by_id('sys_display.to_block')
    elem.click()
    elem.clear()
    elem.send_keys(who_to_inform)



    driver.switch_to.frame(driver.find_element_by_id('message.text_ifr'))
    elem = driver.find_element_by_xpath('//*[@id="tinymce"]')
    elem.clear()
    elem.send_keys(message)
    time.sleep(3)
    driver.switch_to.default_content()
    time.sleep(3)
    elem = driver.find_element_by_id('send_button')
    elem.click()
    time.sleep(3)

def logToTicketSystem():
    '''Login to the ticket system using web browser Firefox'''
    driver = webdriver.Firefox()
    #host='https://opusflow.service-now.com/'
    driver.get(HOST + '/login.do')
    elem=driver.find_element_by_id('user_name')
    elem.clear()
    elem.send_keys(USR)
    elem=driver.find_element_by_id('user_password')
    elem.clear()
    elem.send_keys(PWD)
    submit_button = driver.find_elements_by_id('sysverb_login')[0]
    submit_button.click()
    time.sleep(3)

    return driver

def main():
    
    driver = logToTicketSystem()
    worknotes=''
    logs=''

    lista = getDataFromQueue()
    for element in lista:

        number = element.get('number','')
        sys_id = element.get('sys_id','')
        title = element.get('short_description','')
        description = element.get('description','')
        caller = element.get('caller','')
        company = element.get('company','').get('value','')##
        print(number)
        print(sys_id)
        
        workInProgress(sys_id)
        list_of_attachments = []

        files_text = ''
        if log.exists(number):
            returnToCS(sys_id,CS_XIB,"Hi,this ticket was processed before, please check.")
            continue
        

        who = companies.get(company,'')

        if who:

            if who == 'Pagero' or who == 'CGI' or who == 'Crediflow' or who == 'InExchange':  #  zmiana 19 maj 2020
                ###get attachments, just xmls will be processed
                list_of_attachments = getListOfAttachments(sys_id)
                if list_of_attachments :
                    l = getAttachments(list_of_attachments)
                    files_text = getFilesText(l)
                
                        


            if who == 'CGI' or who == 'InExchange': #  zmiana 19 maj 2020
                if files_text:
                    description = files_text

            if description !='':
                who_to_inform = getAddress(who,title,description) ##### napisane, przetestuj
            else:
                who_to_inform = ''
            
            if who_to_inform !='':
                ###OK wysylamy maila i logujemy ze OK
                if who_to_inform == 'close':
                    closeTicket(sys_id,str('ticket closed')) 
                    log.add_log(number+':'+sys_id+':'+':******************, close ticket')
                    sleep(10)
                else:
                    
                    send_mail(driver , sys_id, description,who_to_inform ) ###napisane, przetestuj, nie dodaje nigdzie plików ? <hahaha>
                    closeTicket(sys_id,str('informed: '+who_to_inform)) 
                    log.add_log(number+':'+sys_id+':'+':processed , closed')
                    sleep(10)
            else:
                returnToCS(sys_id, CS_XIB , 'Hi, couln\'t find contact, return to CS')
                log.add_log(number+':'+sys_id+':'+':couln\'t find contact, return to CS')
                sleep(10)


        else:
            returnToCS(sys_id, CS_XIB , 'Hi, company unrecognized, return to CS')
            log.add_log(number+':'+sys_id+':'+':company unrecognized, return to CS')
            sleep(10)

    
    driver.close()
    driver.quit()

            


        
            
if __name__=='__main__':

    while True:
        main()
        sleep(600)

