#11.06.2019 IADDRESS Module
from bs4 import BeautifulSoup
import DRIVER
import time

def existInIAddress(page): ##tu sprawdzanie czy istnieje czy nie
    soup = BeautifulSoup(page,'lxml')
    t= soup.find_all(class_="even")
    if len(t)>0:
        return t
    else:
        return 'error'


def getData(companyElectronicAddress,driver):
    page = DRIVER.getDataFromIAddress(driver,companyElectronicAddress)
##    time.sleep(60)
    soup = BeautifulSoup(page,'lxml')
    t = soup.find_all('a')
    
    for element in t:
            for i in element.contents:
                if "Click to see all" in i:
                        #print('JEST')
                        e = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/div/div/table/tbody/tr[2]/td/h1/a')
                        e.click()
                        time.sleep(30)
    t = existInIAddress(page)
    lista=list()
    if t!='error':
        for element in t:
            d=dict()
            w= element.find_all('td')
            
            d.update({'org_link':w[0].find('a').get('href')})
            d.update({'site_link':w[1].find('a').get('href')})
            d.update({'site_id':w[2].contents[2].strip(' \n\t')})
            d.update({'electronic_adr':w[3].contents[2].strip(' \n\t')})
            try:
                d.update({'lmc':w[5].find('b').contents[0].strip(' \n\t')})
            except:
                 d.update({'lmc':''})
            try:
                d.update({'status':w[6].contents[0].strip(' \n\t')})
            except:
                d.update({'status':''})

            lista.append(d)
    else:
        #lista.append('empty iaddress')
        return ''
    return lista
        
    
