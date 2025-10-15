##12.07
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import OPERATORS
import OP

#from time import sleep
def getXpath(driver):
    xpath=''
    soup = BeautifulSoup(driver.page_source,'lxml')
    t = soup.find_all('tbody')
    tabela = t[5].find_all('tr')
    for i, element in enumerate(tabela,start=1):
        a=element.find(class_="receiveChannelsChange recChannelStatus")
        if 'bs4' in str(type(a)):
            b = a.find(selected="selected")
            if 'Enabled'== b.string:
                xpath = '/html/body/div/div[3]/div[2]/div/div[1]/table[2]/tbody/tr['+str(i)+']'

    return xpath


def checkIdentifiersNumber(page):
    soup = BeautifulSoup(page,'lxml')


    t = soup.find('table',id='siteIdentifiersTable')

    rows = t.find_all('tr')

    return(len(rows))

def changeSite(driver, siteId, operator, electronic_address ,date,ticket): ##
    oper=operator
    operator = OPERATORS.op.get(oper)

    print(operator)
    
    driver.get("https://iaddress..."+siteId)
    time.sleep(5)
    page = driver.page_source
    ##check how many identyfiers 2019-08-27
    if(checkIdentifiersNumber(page)>2):
        #oddaj do CS z notka
        return 'ERROR'
    #search for one enabled, to at the end disable it

    path = getXpath(driver)
    e_for_disablibg=''
    if path :
        e_for_disablibg= driver.find_element_by_xpath(path+'/td[3]/select')
    e = driver.find_element_by_class_name('addSiteReceiveChannel')
    e.click()
    time.sleep(3)
    ###basic add site, without date
    e = driver.find_element_by_id('lmc')
    select = Select(e)
    select.select_by_visible_text(operator)
    e = driver.find_element_by_id('electronicAddress')
    if "Tieto" in operator:                             ###if Tieto operator only!!
        electronic_address = 'TE'+ electronic_address
    e.send_keys(electronic_address)


    if date:
        pass
    else:
        select = Select(e_for_disablibg)
        select.select_by_visible_text('Disabled')

    element = driver.find_element_by_id('operationTicketId')
    element.send_keys(ticket)

    element = driver.find_element_by_id('operationComment')
    element.send_keys(ticket)

    e= driver.find_element_by_id('saveSite')
    e.click()

    e = driver.find_element_by_id('popup_ok')
    e.click()

    time.sleep(2)
    return 'OK'

def checkCompanyName(driver,ticket,org_link,ovt, ytj_name, of_name):
    url = 'https://iaddress...'+org_link
    driver.get(url)
    time.sleep(3)
    e = driver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div/div[1]/table[1]/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td[1]/input[2]')
    current_name = e.get_attribute('value')

    if len(ovt) == 12:
        if current_name.lower() != ytj_name.lower():
            e.clear()
            e.send_keys(ytj_name)
            e=driver.find_element_by_id('operationTicketId')
            e.clear()
            e.send_keys(ticket)
            e=driver.find_element_by_id('operationComment')
            e.clear()
            e.send_keys(ticket)
            button = driver.find_element_by_id('saveOrganization')
            button.click()
            button = driver.find_element_by_id('popup_ok')
            button.click()
    elif len(ovt) > 12:
        if current_name.lower() != of_name.lower():
            e.clear()
            e.send_keys(of_name)
            e=driver.find_element_by_id('operationTicketId')
            e.clear()
            e.send_keys(ticket)
            e=driver.find_element_by_id('operationComment')
            e.clear()
            e.send_keys(ticket)
            button = driver.find_element_by_id('saveOrganization')
            button.click()
            button = driver.find_element_by_id('popup_ok')
            button.click()
