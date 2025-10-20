import os
from datetime import datetime


class Tools:

    def fileName():
        filename = datetime.today().strftime('%Y-%m-%d') + '_log.txt'
        return filename

    def folderPlusPath():
        currentPath = os.getcwd()
        listOfStuff = os.listdir()

        if not ('LogFolder' in listOfStuff):
            os.mkdir('LogFolder')

        if '\\' in currentPath:

            currentPath = currentPath + '\\' + 'LogFolder' + '\\'
        else:
            currentPath = currentPath + '/' + 'LogFolder' + '/'

        return currentPath


class Logs(Tools):
    def __init__(self):
        self.path = Tools.folderPlusPath()
        self.file = Tools.fileName()

    def addLog(self, log):
        log = datetime.today().strftime('%Y-%m-%d %H:%M') + ' : ' + log + '\n'
        file = self.path + self.file
        with open(file, 'a+') as fp:
            fp.write(log)
