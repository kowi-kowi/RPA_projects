#OF
import conf
import log
import OPERATORS, iAddressOperators
import Scenarios
import requests, json


#####Glob variables

HOST = conf.host
OFUSER = conf.ofusr
OFPWD = conf.ofpwd


CS_GROUP = conf.OC_CS_FI_Customer_Service
ROBOT_GROUP = conf.OC_CS_FI_Customer_Service_Robots

ROGER = conf.sa_rpa_roger

def stripOvt(ovt):
    if '0037' in ovt and 'FI' not in ovt:
        start = ovt.index('0037')
        temp = ovt[start:].strip()
        ovt = temp
        return ovt.replace(' ','')
    elif 'FI' in ovt:
        start = ovt.index('FI')
        temp = ovt[start:].strip()
        ovt = temp
        return ovt.replace(' ','')

def assignToRoger(sys_id):

    url = HOST+'/api/now/table/sc_req_item/'+sys_id
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    d = {'assigned_to':ROGER}

    dane = json.dumps(d)

    response = requests.put(url, auth=(OFUSER, OFPWD), headers=headers ,data=dane)

    if response.status_code != 200:
        return 'ERROR'


def returnToCS(sys_id, message,state): #simple return, if case was already processed, or not B2B request


    url = HOST+'/api/now/table/sc_req_item/'+sys_id
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    work_notes=message

    if state!=0:
        d={"assignment_group":CS_GROUP,"work_notes":work_notes,"state":"8"}
        dane = json.dumps(d)
    else:
        d={"assignment_group":CS_GROUP,"work_notes":work_notes}
        dane = json.dumps(d)

    response = requests.put(url, auth=(OFUSER, OFPWD), headers=headers ,data=dane)

    if response.status_code != 200:
        return 'ERROR'
def informCustomer(sys_id,scenario_number):
    message = Scenarios.messages.get(scenario_number)
    url = HOST+'/api/now/table/sc_req_item/'+sys_id
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    dane = json.dumps({"comments":message})

    response = requests.put(url, auth=(OFUSER, OFPWD), headers=headers ,data=dane)

    if response.status_code != 200:
        return 'ERROR'

def changeStatusAndAddWorknotes(ticket,log,s):
    url = HOST+'/api/now/table/sc_req_item/'+ticket
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    dane = json.dumps({"work_notes":log, "state":s})
    response = requests.put(url, auth=(OFUSER, OFPWD), headers=headers ,data=dane)

    if response.status_code != 200:
        return 'ERROR'

def close(sys_id,scenario_number,status): #07.01.2021 dodanie ptaszka przy disable notification

    message = Scenarios.messages.get(scenario_number)
    url = HOST+'/api/now/table/sc_req_item/'+sys_id
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    s=str(3)
    if status == 4:
        s=str(4)


    dane = json.dumps({"comments":message})
    response = requests.put(url, auth=(OFUSER, OFPWD), headers=headers ,data=dane)

    dane = json.dumps({"close_notes":message, "state":s, "u_disable_notification":"true"})
    response = requests.put(url, auth=(OFUSER, OFPWD), headers=headers ,data=dane)
    

    if response.status_code != 200:
        return 'ERROR'

def getDataFromOpusFlow(url):
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    response=requests.get(url, auth=(OFUSER, OFPWD), headers=headers)

    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        return ''
    return response.json()


def getCasesFromQueue(): #build list of tasks to be processed, first validation, if it is B2B request. If yes add to list, if not
    url = HOST+'/api/now/table/task?sysparm_query='+'assignment_group='+ROBOT_GROUP+'^stateIN-6,1,2,5^numberSTARTSWITHOCRITM^short_descriptionLIKEiAddress' ###check URL
    response = getDataFromOpusFlow(url)
    lista = list()

    if response !='':
        temp = response.get('result',None)
        if temp :
            for element in temp:
                if "Request for new B2B e-invoice routing to iAddress" in element.get('short_description'):
                    lista.append(element.get('sys_id',None))
                    assignToRoger(element.get('sys_id',None))
                else:
                    #oddaj do CS, z informacja, ze to nie jest
                    message = returnToCS(element.get('sys_id',None),'Based on short description, this is not B2B routing request',0)
                    if message == 'ERROR':
                        #zaloguj ze nie mozesz oddac do CS, a to nie jest request B2B
                        log.add_log(element.get('sys_id',None)+':'+element.get('number',None)+':: this is not B2B reques, problem with returning it to CS')
        return lista
    else:
        return lista

def checkIfClose(sys_id):
    
    url = 'servicenowlink/api/now/table/sc_req_item/'+str(sys_id)


    user = 'Maria.Kowalska@opuscapita.com'
    pwd = 'Con-essen1'


    headers = {"Content-Type":"application/json","Accept":"application/json"}


    response = requests.get(url, auth=(user, pwd), headers=headers )


    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()

    # Decode the JSON response into a dictionary and use the data
    data = response.json()
    if 'verkkolasku@onninen.com' == data['result']['sys_created_by']:
        return True
    else:
        return False

def checkLogs(lista):

    temp=lista

    for element in lista:

        sys_id = log.exists(element)
        

        if sys_id:
            decyzja = checkIfClose(sys_id)
            if decyzja:

                 
                url = HOST+'/api/now/table/sc_req_item/'+sys_id
                headers = {"Content-Type":"application/json","Accept":"application/json"}

                dane = json.dumps({"state":str(3)})
                response = requests.put(url, auth=(OFUSER, OFPWD), headers=headers ,data=dane)           
                temp.remove(element)
                
            else:
                returnToCS(element,'This request was already processed, please check it.',0)
                temp.remove(element)
    lista=temp

    return lista

def nuberOfAttachment(sys_id):

    headers = {"Content-Type":"application/json","Accept":"application/json"}
    url=HOST+'/api/now/table/sys_attachment?sysparm_query=table_sys_id%3D'+sys_id
    response = requests.get(url, auth=(OFUSER, OFPWD), headers=headers )

    lista = response.json().get('result','')

    if lista:

        return 1

    else:
        return 0


###not used
def checkOperator(operator):
    if 'opus' not in operator.lower():
        temp = OPERATORS.op.get(operator,'')
        print(operator)
        if temp !='':
            return True
        else:

            return False
    else:
        return False


def getDataFromTask(sys_id):
    url=HOST+'/sc_req_item.do?JSONv2&sysparm_action=getRecords&sysparm_query=sys_id='+sys_id+'&displayvariables=true'
    print(url)
    response = getDataFromOpusFlow(url)

    if response !='':
        var = response['records'][0].get('variables','')
        if var !='':
            l = dict() ###gdzie robic walidacje ?

            ##get and validate caller
            caller = response['records'][0].get('sys_created_by','')
            if caller != '' and 'nordea'  not in caller.lower():

                l.update({'caller':caller})#caller
            else:

                log.add_log(sys_id+'::ERROR, caller Nordea')
                returnToCS(sys_id,'Nordea caller',0)
                return 'ERROR'

            ##add task number and sys_id

            l.update({'number':response['records'][0].get('number','')})#ticket number
            print(l['number'])
            l.update({'sys_id':sys_id})#sys_id

            ##check attachments

            if nuberOfAttachment(sys_id) == 1:
                log.add_log(sys_id+':'+l['number']+':ERROR, some attachments') ###################################
                returnToCS(sys_id,'Task contains attachments',0)
                return 'ERROR'

            ##check country

            country = var[0].get('value','')
            if country.lower() == 'finland':
                l.update({'country':country}) #country Finland
            else:
                log.add_log(sys_id+'::ERROR, it is not form for Finland')
                returnToCS(sys_id,'Other than Finish form was choosen.',0)
                return 'ERROR'

            l.update({'company_name':var[15].get('value','')}) #company name
            l.update({'edira':var[17].get('value','')}) #edira
            number = l['number']
            bi = stripOvt(var[20].get('value',''))
            print('bi przed sripem',var[20].get('value',''),'bi po stripie',bi)
            if not bi:
                print('oddam do CS')
                log.add_log(sys_id+':'+number+':'+'BI='+str(var[20].get('value','')))
                returnToCS(sys_id,'incorect BI '+str(var[20].get('value','')),0)
                return 'ERROR'


            l.update({'busines_id':bi}) #business id company receiving id
            atbc = stripOvt(var[21].get('value',''))
            if not atbc:
                print('oddam do CS')
                log.add_log(sys_id+':'+number+':'+'atbc='+str(var[21].get('value','')))
                returnToCS(sys_id,'incorect atbc '+str(var[21].get('value','')),0)
                return 'ERROR'
            print('przed',var[21].get('value',''),'po ',atbc)
            l.update({'address_tbc':atbc}) #address to be changed company electronic address

            ##get operator
            operator = var[23].get('value','')
            if operator.lower() == 'other':

                log.add_log(sys_id+'::ERROR, unidentify operator') ########################17.01.2020
                returnToCS(sys_id,'Unidentified operator',0)
                return 'ERROR'
                #operator = var[12].get('value','')

            ##check operator on the list
            l.update({'operator':operator})


##            l.update({'operator':var[10].get('value','')})#operator , will be OTHER
##            l.update({'other_operator':var[12].get('value','')})#other operator

            l.update({'date':var[26].get('value','')})#date

            more_info = var[27].get('value','')
            if more_info:
                log.add_log(sys_id+'::ERROR, some additional information in more_info field')
                returnToCS(sys_id,'Additional information from customer',0)
                return 'ERROR'


            return l
        else:
            log.add_log(sys_id+'::ERROR, data could not be taken from variables , empty variables')
            returnToCS(sys_id,'Problem with takeing data from this ticket, empty variables as if this is not B2B task, please check.',0)
            return 'ERROR'

    else:
        log.add_log(sys_id+'::ERROR, data could not be taken from variables')
        returnToCS(sys_id,'Problem with takeing data from this ticket, please check.',0)
        return 'ERROR'
