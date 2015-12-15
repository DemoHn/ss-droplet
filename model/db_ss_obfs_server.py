#coding=utf-8
# last edit: 2015-12-12

from model.model import Database
import traceback
from utils import returnModel

class ssOBFSServerDatabase(Database):
    # ONLY record shadowsocks server info.
    # @param `env` specify the running environment
    # for tests, `env` = "test",
    # and for actual development, `env` = "normal"
    def __init__(self, env="normal"):
        super().__init__()
        self.env = env
        Database.__init__(self,env=self.env)
        self.createTable()
        self.rtn = returnModel()

    def createTable(self):
        # ss database table
        # NOTICE: start_time & expire_time are ALL UTC TIME !!!!!!!!!!!!!!
        try:
            table_str = '''CREATE TABLE IF NOT EXISTS ss_obfs_server(
            service_idf VARCHAR(64) unique,
            server_port text,
            password text
            )'''
            cursor = self.cursor
            cursor.execute(table_str)
            self.connection.commit()
        except:
            return False
        pass

    # while new ss-server (OBFS) created, the first thing, of course is to insert a record
    # into the database

    # @params
    # service_idf : service Identifier. It is the only ID. Generate randomly
    # server_port : shadowsocks service port
    # password    : password for shadowsocks (can be modified by user)
    def insertServerInstance(self,service_idf,server_port,password):
        try:
            insert_str = "INSERT INTO ss_obfs_server VALUES(%s,%s,%s)"

            cursor = self.cursor
            cursor.execute(insert_str,[service_idf,server_port,password])
            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()
            return False
        pass

    # just for debugging==========
    def _readRawData(self):
        select_str = "SELECT * FROM ss_obfs_server"
        c = self.cursor
        c.execute(select_str)
        data = c.fetchall()
        for row in data:
            print(row)

    def getItem(self,service_idf):
        try:
            c = self.cursor
            _str = "SELECT service_idf,server_port,password FROM ss_obfs_server WHERE `service_idf` = %s"
            c.execute(_str,[service_idf])
            _data = c.fetchone()
            self.connection.commit()
            if _data == None:
                return self.rtn.error(500)
            else:
                item = {
                    "service_idf" : _data[0],
                    "server_port" : _data[1],
                    "password"    : _data[2]
                }

                return self.rtn.success(item)
        except:
            traceback.print_exc()
        pass

    def getActiveInstance(self):
        try:
            c = self.cursor
            _str = "SELECT serivce_idf,server_port,password FROM ss_obfs_server"

            c.execute(_str)
            data = c.fetchall()
            self.connection.commit()
            return_arr = []
            for _data in data:
                item = {
                    "service_idf" : _data[0],
                    "server_port" : _data[1],
                    "password"    : _data[2]
                }

                return_arr.append(item)
            return self.rtn.success(return_arr)
        except Exception as e:
            traceback.print_exc()

    def deleteInstance(self,service_idf):
        try:
            c = self.cursor
            delete_str = "DELETE FROM ss_obfs_server WHERE service_idf = %s"
            c.execute(delete_str,[service_idf])
            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()

    # to detect if thte dest_port is already duplicated with another instance
    def portCollision(self,dest_port):
        try:
            c = self.cursor
            port_str = "SELECT service_idf FROM ss_obfs_server WHERE server_port = %s"
            c.execute(port_str,[str(dest_port)])
            self.connection.commit()
            data = c.fetchone()
            if data == None:
                return False
            else:
                return True
        except Exception as e:
            traceback.print_exc()