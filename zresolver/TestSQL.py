#!/usr/bin/python3

import sqlite3

from Settings import Settings


class TestSQL:
    def __init__(self, nameDB, typeDB) -> None:
        self.nameDB = nameDB
        self.typeDB = typeDB
    
    def createConnection(self):
        if self.typeDB == 'sqlite3':
            connection = sqlite3.connect(self.nameDB)
            try:
                connection = sqlite3.connect(self.nameDB)
            except sqlite3.Error as error:
                print("Error =", error)
                Settings().createLogEntry(error)
        return connection
    
    def initDB(self):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                table = """CREATE TABLE hostsIPv4 (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ipv4 TEXT NOT NULL UNIQUE,
                        hostname TEXT NOT NULL,
                        ttl INTEGER);"""

                cursor = connection.cursor()
                cursor.execute(table)

                table = """CREATE TABLE hostsIPv6 (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ipv6 TEXT NOT NULL UNIQUE,
                        hostname TEXT NOT NULL,
                        ttl INTEGER);"""

                cursor = connection.cursor()
                cursor.execute(table)

                connection.commit()
                cursor.close()

            except sqlite3.Error as error:
                print("Error", error)
                Settings().createLogEntry(error)
            finally:
                if (connection):
                    connection.close()
    
    def getDataIPv4(self, hostname):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                query = """SELECT ipv4
                            FROM hostsIPv4
                            WHERE hostname=?"""

                cursor.execute(query, (hostname, ) )                
                output = cursor.fetchone()
                cursor.close()
                if output == None:
                    output = ['0']

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()

        return output
    
    def getDataIPv6(self, hostname):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                query = """SELECT ipv6
                            FROM hostsIPv6
                            WHERE hostname=?"""

                cursor.execute(query, (hostname, ) )                
                output = cursor.fetchone()
                cursor.close()
                if output == None:
                    output = ['0']

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()

        return output

    def getTTLbyNameIPv4(self, hostname):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                query = """SELECT ttl
                            FROM hostsIPv4
                            WHERE hostname=?"""

                cursor.execute(query, (hostname, ) )                
                output = cursor.fetchone()
                cursor.close()
                if output == None:
                    output = ['0']

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()

        return int(output[0])
    
    def getTTLbyNameIPv6(self, hostname):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                query = """SELECT ttl
                            FROM hostsIPv6
                            WHERE hostname=?"""

                cursor.execute(query, (hostname, ) )                
                output = cursor.fetchone()
                cursor.close()
                if output == None:
                    output = ['0']

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()

        return int(output[0])

    def getTTLv4(self, row):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                query = """SELECT ttl
                            FROM hostsIPv4
                            WHERE id=?"""

                cursor.execute(query, (row, ) )                
                output = cursor.fetchone()
                cursor.close()
                if output == None:
                    output = ['0']

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()

        return int(output[0])
    
    def getTTLv6(self, row):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                query = """SELECT ttl
                            FROM hostsIPv6
                            WHERE id=?"""

                cursor.execute(query, (row, ) )                
                output = cursor.fetchone()
                cursor.close()
                if output == None:
                    output = ['0']

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()

        return int(output[0])
    
    def insertDataIPv4(self, ip, hostname, ttl):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()

                data = (ip, hostname, ttl)
                query = """INSERT INTO hostsIPv4
                          (ipv4, hostname, ttl)
                          VALUES (?, ?, ?);"""

                cursor.execute(query, data)
                connection.commit()
                cursor.close()

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()
    
    def insertDataIPv6(self, ip, hostname, ttl):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()

                data = (ip, hostname, ttl)
                query = """INSERT INTO hostsIPv6
                          (ipv6, hostname, ttl)
                          VALUES (?, ?, ?);"""

                cursor.execute(query, data)
                connection.commit()
                cursor.close()

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()
    
    def updateTTLipv4(self, ttl, row):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                sql_update_query = """UPDATE hostsIPv4
                                        SET ttl = ?
                                        WHERE id = ?"""
                data = (ttl, row)
                cursor.execute(sql_update_query, data)
                connection.commit()
                cursor.close()

            except sqlite3.Error as error:
                print("Error", error)
                Settings().createLogEntry(error)
            finally:
                if (connection):
                    connection.close()
                #toLog = "Таблица TTL обновлена для строки {}. Новое значение = {}".format(row, ttl)
                #Settings().createLogEntry(toLog)
            
    def updateTTLipv6(self, ttl, row):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                sql_update_query = """UPDATE hostsIPv6
                                        SET ttl = ?
                                        WHERE id = ?"""
                data = (ttl, row)
                cursor.execute(sql_update_query, data)
                connection.commit()
                cursor.close()

            except sqlite3.Error as error:
                print("Error", error)
                Settings().createLogEntry(error)
            finally:
                if (connection):
                    connection.close()
                #toLog = "Таблица TTL обновлена для строки {}. Новое значение = {}".format(row, ttl)
                #Settings().createLogEntry(toLog)
    
    def deleteRowIPv4(self, hostname):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                sql_update_query = """DELETE FROM hostsIPv4
                                        WHERE hostname = ?"""
                cursor.execute(sql_update_query, (hostname,))
                connection.commit()
                cursor.close()

            except sqlite3.Error as error:
                print("Error", error)
                Settings().createLogEntry(error)
            finally:
                if (connection):
                    connection.close()
                #toLog = "Строка удалена для значения имени {}.".format(hostname)
                #Settings().createLogEntry(toLog)
    
    def deleteRowIPv6(self, hostname):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()
                sql_update_query = """DELETE FROM hostsIPv6
                                        WHERE hostname = ?"""
                cursor.execute(sql_update_query, (hostname,))
                connection.commit()
                cursor.close()

            except sqlite3.Error as error:
                print("Error", error)
                Settings().createLogEntry(error)
            finally:
                if (connection):
                    connection.close()
                #toLog = "Строка удалена для значения имени {}.".format(hostname)
                #Settings().createLogEntry(toLog)
    
    def getCountIPv4(self):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()

                query = """SELECT count(*)
                            FROM hostsIPv4"""

                cursor.execute(query)
                value = cursor.fetchone()
                cursor.close()

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()
        return value
    
    def getCountIPv6(self):
        connection = self.createConnection()
        if self.typeDB == 'sqlite3':
            try:
                cursor = connection.cursor()

                query = """SELECT count(*)
                            FROM hostsIPv6"""

                cursor.execute(query)
                value = cursor.fetchone()
                cursor.close()

            except sqlite3.Error as error:
                print("Error", error)
            finally:
                if (connection):
                    connection.close()
        return value