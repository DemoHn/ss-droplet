__author__ = "Mingchuan"
#coding=utf-8
# last edit: 2015-12-04

from model.model import Database
import traceback
from utils import returnModel, timeUtil

class ssServerDatabase(Database):
    # ONLY record shadowsocks server info.
    # @param `env` specify the running environment
    # for tests, `env` = "test",
    # and for actual development, `env` = "normal"
    def __init__(self,env="normal"):
        self.env = env
        Database.__init__(self,env=self.env)
        self.createTable()
        self.rtn = returnModel()

    def createTable(self):
        # ss database table
        # NOTICE: start_time & expire_time are ALL UTC TIME !!!!!!!!!!!!!!
        try:
            table_str = '''CREATE TABLE IF NOT EXISTS ss_server(
            service_idf VARCHAR(64) unique,
            server_port text,
            password text,
            method text,
            timeout integer
            )'''
            cursor = self.cursor
            cursor.execute(table_str)
            self.connection.commit()
        except:
            return False
        pass

    # while new ss-server created, the first thing, of course is to insert a record
    # into the database

    # @params
    # service_idf : service Identifier. It is the only ID. Generate randomly
    # server_port : shadowsocks service port
    # password    : password for shadowsocks (can be modified by user)
    # method      : crypt method for shadowsocks (can be modified by user)
    # timeout     : shadowsocks parameter (timeout)
    def insertServerInstance(self,service_idf,server_port,password,method,timeout):
        try:
            insert_str = "INSERT INTO ss_server VALUES(%s,%s,%s,%s,%s)"

            cursor = self.cursor
            cursor.execute(insert_str,[service_idf,server_port,password,method,int(timeout)])
            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()
            return False
        pass

    # just for debugging==========
    def _readRawData(self):
        select_str = "SELECT * FROM ss_server"
        c = self.cursor
        data = c.execute(select_str)
        self.connection.commit()
        for row in data:
            print(row)

    def getItem(self,service_idf):
        try:
            c = self.cursor
            _str = "SELECT service_idf,server_port,password,method,timeout FROM ss_server WHERE `service_idf` = %s"
            data = c.execute(_str,[service_idf])
            _data = c.fetchone()
            self.connection.commit()
            if _data == None:
                return self.rtn.error(500)
            else:
                item = {
                    "service_idf" : _data[0],
                    "server_port" : _data[1],
                    "password"    : _data[2],
                    "method"      : _data[3],
                    "timeout"     : _data[4]
                }

                return self.rtn.success(item)
        except:
            traceback.print_exc()
        pass

    def getActiveInstance(self):
        try:
            c = self.cursor
            _str = "SELECT serivce_idf,server_port,password,method,timeout FROM ss_server"

            data = c.execute(_str)
            self.connection.commit()
            return_arr = []
            for _data in data:
                item = {
                    "service_idf" : _data[0],
                    "server_port" : _data[1],
                    "password"    : _data[2],
                    "method"      : _data[3],
                    "timeout"     : _data[4]
                }

                return_arr.append(item)
            return self.rtn.success(return_arr)
        except Exception as e:
            traceback.print_exc()

    def deleteInstance(self,service_idf):
        try:
            c = self.cursor
            delete_str = "DELETE FROM ss_server WHERE service_idf = %s"
            c.execute(delete_str,[service_idf])
            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()

    # to detect if thte dest_port is already duplicated with another instance
    def portCollision(self,dest_port):
        try:
            c = self.cursor
            port_str = "SELECT service_idf FROM ss_server WHERE server_port = %s"
            c.execute(port_str,[str(dest_port)])
            data = c.fetchone()
            self.connection.commit()
            if data == None:
                return False
            else:
                return True
        except Exception as e:
            traceback.print_exc()