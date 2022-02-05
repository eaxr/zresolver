#!/usr/bin/python3

import socket, threading, asyncio

from random import randint
from queue import Queue
from binascii import unhexlify

from TestParseDNS import TestParseDNS
from Settings import Settings
from TestSQL import TestSQL
from TestSQL import TestSQL


class TestResolverProtocolFactory:
    '''
    Класс обработки запросов и отправки результатов
    '''
    def __init__(self, loop):
        self.loop = loop

    def connection_made(self, transport):
        self.transport = transport
    
    def to_masterdns(self, message, address, port, queue):
        event = threading.Event()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(message, (address, port))
            data, _ = sock.recvfrom(4096)
        finally:
            sock.close()
        queue.put((data, event))
    
    def to_masterdns_t(self, message, address, port, queue):
        for adr in address:
            searchThread = threading.Thread(target=self.to_masterdns, args=(message, adr, port, queue))
            searchThread.start()
        
        data, event = queue.get()
        event.set()
        queue.task_done()

        return data

    def datagram_received(self, data, addr):
        # Обработка сообщения и отправка результата
        self.loop.create_task( runResolverAnswer(self.loop, self.transport, data, addr) )

    def res_answer(self, data, addr):
        # Отправка ответа
        self.transport.sendto(data, addr)

async def runResolver(loop):
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: TestResolverProtocolFactory(loop),
        local_addr=(
            Settings().resolverIP,
            Settings().resolverPORT))

async def runSearchDNS(loop, data):
    hostname = ''
    ip = ''
    toSend = b''
    parseQuestion = TestParseDNS(data)
    for element in parseQuestion.dnsQuestion[:-2]:
        hostname += element
    
    queuetype = parseQuestion.dnsQuestion[-2:-1][0]
    resultDB, resultTTL = await runResolverDB(loop, hostname, queuetype)

    toLog = "TEST, Сообщение запроса поиска. Заголовок: {}, Запрос: {}".format(
        parseQuestion.dnsHeader,
        parseQuestion.dnsQuestion
        )
    print(toLog)
    Settings().createLogEntry(toLog)

    dnsheader = parseQuestion.dnsCreateHeaderAnswer(
            parseQuestion.dnsHeader[0],
            parseQuestion.dnsHeader[9],
            1,
            parseQuestion.dnsQuestion[:-2],
            parseQuestion.dnsQuestion[-2:-1],
            parseQuestion.dnsQuestion[-1:]
    )

    #toLog = "Поиск по имени = {}, Результат поиска в базе данных = {}".format(resultDB, hostname)
    #Settings().createLogEntry(toLog)

    if resultDB[0] == '0':
        resultQ = await runResolverQuestion(loop, data)
        
        parseToStore = TestParseDNS(resultQ)
        dnsRDATA = parseToStore.dnsRDATA
        if len(dnsRDATA[0]) == 8:
            ip = parseToStore.dnsGetIPv4(dnsRDATA)
            ttl = parseToStore.dnsTTL[0]
            await updateResolverDB(loop, ip, hostname, ttl, queuetype)

            #toLog = "Совпадений с именем нет, обращение к вышестоящему dns. Найдено = {}".format(ip)
            #Settings().createLogEntry(toLog)
            #toLog = "Найденный адрес IPv4 сохранен"
            #Settings().createLogEntry(toLog)
        
        elif len(dnsRDATA[0]) == 32:
            ip = parseToStore.dnsGetIPv6(dnsRDATA)
            ttl = parseToStore.dnsTTL[0]
            await updateResolverDB(loop, ip, hostname, ttl, queuetype)

            #toLog = "Совпадений с именем нет, обращение к вышестоящему dns. Найдено = {}".format(ip)
            #Settings().createLogEntry(toLog)
            #toLog = "Найденный адрес IPv6 сохранен"
            #Settings().createLogEntry(toLog)
        
        toSend = resultQ

        toLog = "TEST, Сообщение от вышестоящего dns: {}".format(toSend)
        print(toLog)
        Settings().createLogEntry(toLog)

    elif resultDB[0] != '0' and resultTTL == 0:
        dnsbody = parseQuestion.dnsCreateBody(
                parseQuestion.dnsQuestion[-2:-1],
                resultDB,
                resultTTL
        )

        toSend = dnsheader + dnsbody


        toLog = "TEST, Сообщение из базы данных: {}".format(toSend)
        print(toLog)
        Settings().createLogEntry(toLog)

        if queuetype == 1:
            TestSQL(Settings().nameDB, Settings().typeDB).deleteRowIPv4(hostname)
        elif queuetype == 28:
            TestSQL(Settings().nameDB, Settings().typeDB).deleteRowIPv6(hostname)

        #toLog = "В базе найдено значение, но оно устаревает. Найдено = {}. Значение удалено.".format(resultDB)
        #Settings().createLogEntry(toLog)
    else:
        dnsbody = parseQuestion.dnsCreateBody(
                parseQuestion.dnsQuestion[-2:-1],
                resultDB,
                resultTTL
        )

        toSend = dnsheader + dnsbody

        toLog = "TEST, Сообщение из базы данных: {}".format(toSend)
        print(toLog)
        Settings().createLogEntry(toLog)

        toLog = "В базе найдено значение. Найдено = {}".format(resultDB)
        Settings().createLogEntry(toLog)

    return toSend
        
async def runResolverQuestion(loop, data):
    queue = Queue()
    result = TestResolverProtocolFactory(loop).to_masterdns_t(data, Settings().masterDNS, 53, queue)
    return result

async def runResolverDB(loop, hostname, queuetype):
    if queuetype == 1:
        name = TestSQL(
            Settings().nameDB,
            Settings().typeDB
            ).getDataIPv4(hostname)
        ttl = TestSQL(
            Settings().nameDB,
            Settings().typeDB
            ).getTTLbyNameIPv4(hostname)
    elif queuetype == 28:
        name = TestSQL(
            Settings().nameDB,
            Settings().typeDB
            ).getDataIPv6(hostname)
        ttl = TestSQL(
            Settings().nameDB,
            Settings().typeDB
            ).getTTLbyNameIPv6(hostname)
    return name, ttl

async def updateResolverDB(loop, ip, hostname, ttl, queuetype):
    if queuetype == 1:
        return TestSQL(
            Settings().nameDB,
            Settings().typeDB
            ).insertDataIPv4(ip, hostname, ttl)
    elif queuetype == 28:
        return TestSQL(
            Settings().nameDB,
            Settings().typeDB
            ).insertDataIPv6(ip, hostname, ttl)

async def runResolverAnswer(loop, *args):
    transport = args[0]
    data = args[1]
    address = args[2]

    result = await loop.create_task(runSearchDNS(loop, data))
    transport.sendto(result, address)

async def updateDBipv4(ttlUpdate, row):
    basettl = TestSQL(Settings().nameDB, Settings().typeDB).getTTLbyNameIPv4(row)
    if basettl > 0:
        basettl -= ttlUpdate
    else:
        basettl = 0
    TestSQL(Settings().nameDB, Settings().typeDB).updateTTLipv4(basettl, row)

async def updateDBipv6(ttlUpdate, row):
    basettl = TestSQL(Settings().nameDB, Settings().typeDB).getTTLbyNameIPv6(row)
    if basettl > 0:
        basettl -= ttlUpdate
    else:
        basettl = 0
    TestSQL(Settings().nameDB, Settings().typeDB).updateTTLipv6(basettl, row)

async def runDBipv4(loop, ttlUpdate):
    # Для изменения TTL записей хранящихся в базе
    # Получаем количество строк
    # Обновляем TTL
    rows = (TestSQL(Settings().nameDB, Settings().typeDB).getCountIPv4())[0]
    for future in asyncio.as_completed([updateDBipv4(ttlUpdate, i+1) for i in range(rows)]):
        await future
    
async def runDBipv6(loop, ttlUpdate):
    # Для изменения TTL записей хранящихся в базе
    # Получаем количество строк
    # Обновляем TTL
    rows = (TestSQL(Settings().nameDB, Settings().typeDB).getCountIPv6())[0]
    for future in asyncio.as_completed([updateDBipv6(ttlUpdate, i+1) for i in range(rows)]):
        await future

async def main():
    loop = asyncio.get_running_loop()
    try:
        toLog = "Resolver up and listening, IP Adress: {}, Port: {}".format(
            Settings().resolverIP,
            Settings().resolverPORT)

        print(toLog)
        Settings().createLogEntry(toLog)

        await loop.create_task(runResolver(loop))
        while True:
            ttlUpdate = 5
            await asyncio.sleep(ttlUpdate)
            await runDBipv4(loop, ttlUpdate)
            await runDBipv6(loop, ttlUpdate)

    finally:
        toLog = "Resolver stopped"
        print(toLog)
        Settings().createLogEntry(toLog)

if __name__ == "__main__":
    # Первоначальный запуск базы данных
    # Создание основной таблицы
    TestSQL(
        Settings().nameDB,
        Settings().typeDB
    ).initDB()

    # Запуск программы
    asyncio.run(main())