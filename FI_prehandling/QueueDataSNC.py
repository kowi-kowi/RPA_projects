from BasicSNC import BasicSNC
class QueueDataSNC(BasicSNC):
    def queue(self,host,table,query):
        list_=list()
        url = host +'/api/now/table/'+table+'?sysparm_query='+query
        print(url)
        response = BasicSNC.sncget(self,url)
        response = response.get('result','')
        for element in response:
            lista.append(element.get('sys_id',''))


        return list_



