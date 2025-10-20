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
import dill


if __name__ == '__main__':
    f=open('start_file','rb'); start = dill.load(f); f.close()
    start()
