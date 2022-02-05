#!/usr/bin/python3

from random import randint
from binascii import unhexlify


class TestParseDNS:
    '''
    Класс для обработки сообщения, которое поступает в байт-коде
    '''
    def __init__(self, message) -> None:
        self.dnsControlformat = [1, 4, 1, 1, 1, 1, 3, 4] # Формат флагов, количество бит для каждого флага
        self.message = message
        self.dnsHeader = []
        self.dnsQuestion = []
        self.dnsBody = []
        self.dnsRDATA = ''
        self.dnsTTL = 0
        self.run()

    def extractBits(self, hex, format) -> bytes:
        result = []
        bsize, bscale,  = 8, 16
        bitstring = ''
        for index, i in enumerate(range(0, (len(hex)-1), 2)):
            bitstring += bin(int(hex[i:i+2], bscale))[2:].zfill(bsize)

        for size in format:
            result.append(bitstring[:size])
            bitstring = bitstring[size:]

        return result
    
    def questionSize(self, dnsBody) -> int:
        a = 1
        msg = 0
        questionFormat = []
        while a != 0:
            a = int(dnsBody[msg:msg+2], 16)
            msg += (a * 2) + 2
            questionFormat.append(a)

        return msg+8, questionFormat[0:-1]

    def questionName(self, dnsBody, questionFormat) -> list:
        result = []
        position = 2
        for a in questionFormat:
            name = ""
            for b in range(position, position+(a*2), 2):
                name += bytearray.fromhex(dnsBody[b:b+2]).decode()
            position += (a * 2) + 2
            result.append(name)
            result.append(".")

        return result[:-1]

    def combineBits(self, dnsBody) -> int:
        stringlen = int(len(dnsBody) / 2)
        a = int(dnsBody[:stringlen], 16)
        b = int(dnsBody[stringlen:], 16)
        return (lambda a, b: a + b)(a, b)

    def dnsQuery(self, dnsQuestion):
        self.dnsBody = dnsQuestion

    def dnsResponse(self, dnsBody, dnsQuestion, dnsQuestionsize):
        # Обработка области данных сообщения
        # Resource record format
        dnsRRsize = dnsQuestionsize + 12

        dnsRR = [dnsBody[dnsQuestionsize:dnsRRsize-10], \
            int(dnsBody[dnsQuestionsize+2:dnsRRsize-8], 16), \
            self.combineBits(dnsBody[dnsQuestionsize+4:dnsRRsize-4]), \
            self.combineBits(dnsBody[dnsQuestionsize+8:dnsRRsize])]

        dnsTTLsize = dnsRRsize + 8
        dnsTTL = [int(dnsBody[dnsRRsize:dnsTTLsize], 16)]

        dnsRDLENGTH = int(dnsBody[dnsTTLsize:dnsTTLsize+4], 16)
        dnsStartrdata = dnsTTLsize + 4
        dnsEndrdata = dnsStartrdata + (dnsRDLENGTH * 2)

        dnsRDATA = [dnsBody[dnsStartrdata:dnsEndrdata]]
   
        self.dnsTTL = dnsTTL
        self.dnsRDATA = dnsRDATA
        self.dnsBody = dnsQuestion + dnsRR + dnsTTL + dnsRDATA
    
    def dnsGetIPv4(self, dnsRDATA):
        result = ''
        raw = dnsRDATA[0]
        for i in range(0, len(raw), 2):
            a = int((raw[i:i+2]), 16)
            result += str(a) + "."
        return result[:-1]
    
    def dnsGetIPv6(self, dnsRDATA):
        result = ''
        raw = dnsRDATA[0]
        for i in range(0, len(raw), 4):
            result += raw[i:i+4] + ":"
        return result[:-1]

    def dnsCreateID(self):
        return format(randint(1, 65535), 'x')
    
    def dnsExapandHex(self, value, size):
        if type(value) == int:
            result = format(value, 'x')
            while len(result) < size:
                result = '0' + result
        elif type(value) == str:
            result = ''
            while len(result) < size:
                result = '0' + result
        return result

    def dnsHotsnameToHex(self, hostname):
        result = ''
        for i in hostname:
            if i != '.':
                result += self.dnsExapandHex(len(i), 2) \
                            + "".join("{:02x}".format(ord(c)) for c in i)
        
        return result + '00'

    def dnsCreateHeaderAnswer(self, *args):
        dnsID = self.dnsExapandHex(args[0], 4)
        dnsFLAGS = self.dnsExapandHex(0x8180, 4)
        dnsQDCOUNT = self.dnsExapandHex(args[1], 4)
        dnsANCOUNT = self.dnsExapandHex(args[2], 4)
        dnsNSCOUNT = self.dnsExapandHex(0x0000, 4)
        dnsARCOUNT = self.dnsExapandHex(0x0000, 4)
        dnsQuestion = self.dnsHotsnameToHex(args[3])
        dnsQTYPE = self.dnsExapandHex(args[4][0], 4)
        dnsQCLASS = self.dnsExapandHex(args[5][0], 4)

        bytestring = unhexlify(dnsID) \
                    + unhexlify(dnsFLAGS) \
                    + unhexlify(dnsQDCOUNT) \
                    + unhexlify(dnsANCOUNT) \
                    + unhexlify(dnsNSCOUNT) \
                    + unhexlify(dnsARCOUNT) \
                    + unhexlify(dnsQuestion) \
                    + unhexlify(dnsQTYPE) \
                    + unhexlify(dnsQCLASS)
        
        return bytestring
    
    def dnsCreateIPv4(self, answertype, answerip, answerttl):
        rr = self.dnsExapandHex(0xc00c, 4)
        result = ''

        for element in answerip:
            rawip = element.split(".")
            result += rr + self.dnsExapandHex(answertype, 4) \
                            + self.dnsExapandHex(0x0001, 4) \
                            + self.dnsExapandHex(answerttl, 8) \
                            + self.dnsExapandHex(0x0004, 4)
            for octet in rawip:
                result += self.dnsExapandHex(int(octet), 2)

        return result
    
    def dnsCreateIPv6(self, answertype, answerip, answerttl):
        rr = self.dnsExapandHex(0xc00c, 4)
        result = ''

        for element in answerip:
            rawip = element.split(":")
            result += rr + self.dnsExapandHex(answertype, 4) \
                            + self.dnsExapandHex(0x0001, 4) \
                            + self.dnsExapandHex(answerttl, 8) \
                            + self.dnsExapandHex(0x0010, 4)

            for double in rawip:
                result += double

        return result

    def dnsCreateBody(self, *args):
        answertype = args[0][0]
        answerip = args[1]
        answerttl = args[2]
        result = ''

        if answertype == 1:
            print("Тип запроса 1, формирование IPv4 адреса")
            result = self.dnsCreateIPv4(answertype, answerip, answerttl)
        elif answertype == 28:
            print("Тип запроса 28, формирование IPv6 адреса")
            result = self.dnsCreateIPv6(answertype, answerip, answerttl)

        return unhexlify(result)

    def run(self):
        '''
        Основной цикл обработки dns сообщения
        '''
        dnsMessage = (self.message).hex()

        # Обработка заголовка
        # Header section format
        dnsHeader = [int(dnsMessage[0:4], 16)] \
                    + self.extractBits(dnsMessage[4:8], self.dnsControlformat) \
                    + [int(dnsMessage[8:12], 16)] \
                    + [int(dnsMessage[12:16], 16)] \
                    + [int(dnsMessage[16:20], 16)] \
                    + [int(dnsMessage[20:24], 16)]

        self.dnsHeader = dnsHeader

        # Обработка сообщения, вывод запроса, типа и класса запроса
        # Question section format
        dnsBody = dnsMessage[24:]

        dnsQuestionsize, questionFormat = self.questionSize(dnsBody)
        dnsQuestion = self.questionName(dnsBody[0:dnsQuestionsize-8], questionFormat) \
            + [self.combineBits(dnsBody[dnsQuestionsize-8:dnsQuestionsize-4])] \
            + [self.combineBits(dnsBody[dnsQuestionsize-4:dnsQuestionsize])]
        
        self.dnsQuestion = dnsQuestion

        # Если QR равен 0, то запрос на поиск dns записи
        # Если код равен 1, то это ответ после поиска
        if int(dnsHeader[1]) == 0:
            self.dnsQuery(dnsQuestion)
        else:
            self.dnsResponse(dnsBody, dnsQuestion, dnsQuestionsize)

        return 0