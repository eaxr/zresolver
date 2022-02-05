#!/usr/bin/python3

import sys, logging, configparser

from random import randint
from binascii import unhexlify


class Configure:
    def __init__(self, path) -> None:
        self.config = configparser.ConfigParser()

        self.config.read(path)
        self.resolverIP     = self.config['BASE']['resolverIP']
        self.resolverPORT   = int(self.config['BASE']['resolverPORT'])
        self.masterDNS      = (self.config['BASE']['masterDNS']).split(", ")
        self.logfile        = self.config['BASE']['logfile']
        self.nameDB         = self.config['BASE']['nameDB']
        self.typeDB         = self.config['BASE']['typeDB']

class Settings:
    '''
    Класс задание параметров работы программы
    '''
    def __init__(self) -> None:
        # Считывание основных параметров
        # Тип подключения, название базы данных
        configurePath=sys.argv[1]
        configure =Configure(configurePath)

        # 0.0.0.0 для запуска без прокси
        self.resolverIP = configure.resolverIP
        self.resolverPORT = configure.resolverPORT
        # 192.168.0.99 - несуществующий адрес, для проверки отправки первого поступившего ответа
        #self.masterDNS = ["192.168.0.99", "8.8.8.8", "1.1.1.1"]
        self.masterDNS = configure.masterDNS
        self.logfile = configure.logfile
        self.nameDB = configure.nameDB
        self.typeDB = configure.typeDB

    @property
    def resolverIP(self):
        return self._resolverIP
    
    @property
    def resolverPORT(self):
        return self._resolverPORT
    
    @property
    def masterDNS(self):
        return self._masterDNS
    
    @property
    def logfile(self):
        return self._logfile
    
    @resolverIP.setter
    def resolverIP(self, ip):
        self._resolverIP = ip
    
    @resolverPORT.setter
    def resolverPORT(self, port):
        self._resolverPORT = port
    
    @masterDNS.setter
    def masterDNS(self, ip):
        self._masterDNS = ip
    
    @logfile.setter
    def logfile(self, path):
        self._logfile = path
    
    def createLogEntry(self, message) -> None:
        logging.basicConfig(filename = self.logfile,
                            filemode = "w",
                            format = "%(levelname)s %(asctime)s - %(message)s", 
                            level = logging.INFO)

        logging.info(message)