import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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

emailRegex = re.compile(r'''(
    [a-zA-Z0-9._%+-]+
    @
    [a-zA-Z0-9._]+
    (\.[a-zA-Z]{2,4})
)''', re.VERBOSE)

CS_SE_QUEUE = conf.OC_CS_SE_Application_Support_Digitizing
EXELA_QUEUE =conf.EXELA_Support_Team
SE_ROBOT_QUEUE = conf.OC_CS_SE_Application_Support_Digitizing_Robot


extension={
        '.png':'image/png',
        '.jpg':'image/jpg',
        '.jpeg':'image/jpg',
        '.tiff':'image/tif',
        '.tif':'image/tif',
        '.Tif':'image/tif',
        '.txt':'text/plain',
        '.xml':'text/xml',
        '.doc':'application/msword',
        '.docx':'application/msword',
        '.dot':'application/msword',
        '.dotx':'application/msword',
        '.xls':'application/msexcel',
        '.xlsx':'application/msexcel',
        '.csv':'application/msexcel',
        '.zip':'application/zip',
        '.eml':'application/email',
        '.msg':'application/email',
        '.pdf':'application/pdf',
        '.PDF':'application/pdf',
        '.htm':'text/html',
        '.html':'text/html',
        }
TaskErrorType={
    '1':'1 - Critical – Other',
    '2':'2 - High – Other',
    '3':'3 - Moderate – Other',
    '4':'4 - Low – Other',
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
        sleep(10)
        
    lista=response.json()['result']

    for element in lista:
        d=dict()
        d.update({'sys_id': element.get('sys_id','')})
        d.update({'file_name':element.get('file_name','')})
        l.append(d)

    

    return l


def checkTmpFolder():
    lista = os.listdir()

    exist ='no'

    for element in lista:
        if element == 'tmp':
            exist = 'yes'
    if exist == 'no':
        os.mkdir('tmp')

def goToTmp():

    path = os.getcwd()
    if 'tmp' not in path:
        os.chdir('tmp')

def exitTmp():
    
    path = os.getcwd()
    if 'tmp' in path:
        os.chdir('..')
def cleanTmp():

    
    goToTmp()

    listOfFiles= os.listdir()

    for file in listOfFiles:
        os.remove(file)
    
def getAttachments(lista1):
 
    checkTmpFolder()
    #cleanTmp()
    goToTmp()

    for element in lista1:
        if element.get('file_name')!='': ###przygladaj sie!!!, przetestuj pozniej
            h= {"Content-Type":"application/xml","Accept":"*/*"}
            u=HOST+"/api/now/attachment/"+element.get('sys_id')+"/file"
            r = requests.get(u, auth=(USR, PWD), headers=h )
            handle = open(element.get('file_name'), "wb")

            for chunk in r.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    handle.write(chunk)
            handle.close()

    sleep(100)
    exitTmp()

        

#upload one attachment to the vendors task
def postAttachments(task,lista_plikow):
    goToTmp()

    for element in lista_plikow:
        file_name, file_extension = os.path.splitext(element)

        fe = file_extension.lower()
        u_ext = extension.get(fe,'')

        

        if u_ext:

            url = HOST+'/api/now/attachment/upload'
            payload = {'table_name':'incident_task', 'table_sys_id':task}

            f=element
            f=unicodedata.normalize('NFKD', f).encode('ascii','ignore')
            s=f.decode("utf-8")
##            s = s.replace(',','')
##            s = s.replace('/','')
            files = {'file': (s, open(element, 'rb'), u_ext, {'Expires': '0'})}
            
            headers = {"Accept":"*/*"}

            
            response = requests.post(url, auth=(USR,PWD), headers=headers, files=files , data=payload)
            

            # Check for HTTP codes other than 201
            if response.status_code != 201:
                continue
        else:
            continue

    exitTmp()

    
    
    
    
def copyAttachments(inc,task):

    l = getListOfAttachments(inc)
    n = 0 ##tyczasowy time stamp

    for element in l:
        
        element['file_name'] = str(n)+'_'+element['file_name'].replace('/','')
        

    if l:
        getAttachments(l)

        lista=list()

        for element in l:
            lista.append(element.get('file_name'))
        
        postAttachments(task,lista)
        sleep(20)
def zbierajMaile(tekst):
    gdzie = []
    for groups in emailRegex.findall(tekst):
        gdzie.append(groups[0])

    return gdzie

def podmien(lista_maili_przed,lista_maili_po, tekst):
   
    for i , element in enumerate(lista_maili_po):
        
        tekst = tekst.replace(element, lista_maili_przed[i])

    return tekst

def doNotTranslateEmails(text_before, text_after):
    emailRegex = re.compile(r'''(
        [a-zA-Z0-9._%+-]+
        @
        [a-zA-Z0-9._]+
        (\.[a-zA-Z]{2,4})
    )''', re.VERBOSE)
    
    lista_maili_przed = zbierajMaile(text_before)
    lista_maili_po = zbierajMaile(text_after)

    return podmien(lista_maili_przed,lista_maili_po, text_after)
    
def MS_translate(text):
    
    subscriptionKey = 'API_KEY'

    base_url = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = '&from=sv&to=en'
    constructed_url = base_url + path + params


    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    t=text
    if "Powered by Basware" in t:
        index = t.index('Powered by Basware')
        t = t[0:index]
    #print(t)
    body = [{
        'text' : t
    }]


    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()


    t=json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False, separators=(',', ': '))

    i=t.find('\"text\":')
    j=t.find('\"to\"')

    #return t[i+9:j-2].strip()[0:-2]
    print(request.status_code)
    if request.status_code == 400:
        return 'ERROR'
    else:
        text_before = t
        text_after = response[0]['translations'][0]['text']
        return doNotTranslateEmails(text_before, text_after)

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

def returnAsAwaiting3rdParty(sys_id, weherReturn):
    url=HOST+'/api/now/table/incident/'+sys_id
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    d=json.dumps({"assignment_group":weherReturn,"u_owner":weherReturn,"assigned_to":"", "state":"-5"})
    response = requests.put(url, auth=(USR,PWD), headers=headers ,data=d)
		 
    if response.status_code != 200: 
        return 'ERROR'

def workInProgress(sys_id):

    url=HOST+'/api/now/table/incident/'+sys_id
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    d=json.dumps({"assigned_to":conf.SA_RPA_roger,"state":"-6"})
    response = requests.put(url, auth=(USR,PWD), headers=headers ,data=d)


def createDescription(t1,t2):
    delimiter = '--'*20
    text = t1+'\n'+ delimiter+'\n'+t2

    return text

def createTask(number,sys_id,EXELA_QUEUE,title,task_description,caller,impact,urgency,prio,company):

    url = HOST + '/api/now/table/incident_task'
    headers = {"Content_Type":"application/json","Accept":"application/json"}

    u_error_type = TaskErrorType.get(prio,'')

    if not u_error_type:
        u_error_type='4 - Low - Other'
    
    if title.strip() =='':
        title = number
        

    d = json.dumps({"assignment_group":EXELA_QUEUE, "incident_task": sys_id, "short_description": title, "description":task_description, "task_for": caller,"impact": impact, "urgency": urgency, "u_error_type":u_error_type,"company":company})

    response = requests.post(url, auth=(USR,PWD), headers=headers,data=d)

    if response.status_code == 400:
        log.add_log(number+':task creation error')

    return response.json()['result']['sys_id']


def main():
    
    
    worknotes=''
    logs=''

    lista = getDataFromQueue()
    for element in lista:

        number = element.get('number','')
        sys_id = element.get('sys_id','')
        title = element.get('short_description','')
        description = element.get('description','')
        impact = element.get('impact','')
        urgency = element.get('urgency','')
        prio = element.get('priority','')
        company = element.get('company','').get('value','')##
        caller = element.get('caller_id','').get('value','')
        print(caller)
        print(number)
        
        workInProgress(sys_id)
        if log.exists(number):
            returnToCS(sys_id,CS_SE_QUEUE,"Hi,this ticket was processed before, please check.")
            continue
        

        if title:
            translate_title = MS_translate(title)
        else:
            translate_title = title

        if description:
            translate_description = MS_translate(description)
        else:
            translate_description = description
        
        if translate_title =='ERROR' or translate_description =='ERROR':
            returnToCS(sys_id,CS_SE_QUEUE,"Translation problem, please hadle manually. I will figure out later what went wrong.")
            log.add_log(number+':translation ERROR')

        else:
    
            task_description = createDescription(translate_title,translate_description)
            task_id=createTask(number,sys_id,EXELA_QUEUE,title,task_description,caller,impact,urgency,prio,company)


        
            copyAttachments(sys_id,task_id)
            returnAsAwaiting3rdParty(sys_id, CS_SE_QUEUE)

        
            log.add_log(number+':'+sys_id+':'+':processed , company = '+company)
            sleep(10)

if __name__=='__main__':
    
    while True:
        
    main()
