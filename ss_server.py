#! /usr/bin/env python
# encoding:utf-8

import sys,os,re
import subprocess
import time
import sqlite3
from datetime import datetime
from string import Template
from multiprocessing import Process
import signal
import traceback

class timeUtil:
    def __init__(self):
        pass

    @staticmethod
    def getCurrentUTCtimestamp():
        # get timestamp
        # time.timezone represents for the seconds that current timestamp delayed
        return int(time.time()) + int(time.timezone)

    @staticmethod
    def getReadableTime(utc_timestamp,timezone):
        # final string e.g: 2015-10-12 17:39
        # here, timezone means hours before UTC
        # e.g: CST <--> +8
        _timestamp = int(utc_timestamp) + int(timezone)*3600

        return datetime.fromtimestamp(_timestamp).strftime("%Y-%m-%d %H:%M:%s")

    @staticmethod
    def getUTCtimestamp(readable_time,timezone):
        # here, timezone means hours before UTC
        # e.g: CST <--> +8
        re_str = "([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+)"
        m = re.search(re_str,readable_time)

        if m == None:
            return False
        else:
            year   = m.group(1)
            month  = m.group(2)
            date   = m.group(3)
            hour   = m.group(4)
            minute = m.group(5)

            dm     = datetime(int(year),int(month),int(date),int(hour),int(minute))
            tm     = time.mktime(dm.timetuple())
            return int(tm) - timezone * 3600

class ssProcess:
    def __doc__(self):
        """
        control shadowsocks process
        """

    def __init__(self):
        self.local_port = 1080
        self.NAME = "ss-server"
        pass

    def get_file_directory(self):
        full_path = os.path.realpath(__file__)
        path,file = os.path.split(full_path)
        return path

    def execCommand(self,cmd,outdir):
        p = subprocess.Popen(cmd,shell=True,stdout = outdir,stderr = subprocess.STDOUT)
        return p.pid

    def execOut(self,cmd):
        p = subprocess.Popen(cmd,shell=True, stdout= subprocess.PIPE)
        (out,err) = p.communicate()
        return out

    def getIP(self):
        # "ifconfig" lists lots of information about IP address and other network configuration
        # we get domestic IP from here
        eth0_data = self.execOut("ifconfig eth0")

        re_ip = "inet addr:([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"

        # if can't read proper info
        if eth0_data.find("inet addr") > 0:
            m = re.search(re_ip,eth0_data)
            return m.group(1)
        else:
            print "[LOG] get IP Error"
            return False
        pass

    def checkProcess(self,port=None):
        process = []
        if port == None:
            cmd = "netstat -putan | grep LISTEN | grep ss-server"
        else:
            cmd = "netstat -putan | grep LISTEN | grep ss-server | grep "+str(port)
        info = self.execOut(cmd)
        info_arr = info.split("\n")[:-1]

        for i in info_arr:
            process_model = {
                "pid":0,
                "port":0
            }
            i_arr = i.split()
            i_process = i_arr[6].split("/")

            ii_pid   = i_process[0]
            ii_pname = i_process[1]

            if ii_pname == "ss-server":
                process_model['pid'] = ii_pid
                process_model['port'] = i_arr[3].split(":")[1]
                process.append(process_model)

        return process

    def createProcess(self,port,password,timeout=100,method="rc4-md5"):

        HOST_IP = ""

        if not self.getIP():
            return False
        else:
            HOST_IP = self.getIP()

        # kill the "ss" process if the port has been occupied (sometimes for restart the process)
        pid_array = self.checkProcess()
        for i in pid_array:
            if str(i['port']) == str(port):
                self.killProcess(int(i['pid']))

        cmd_content = Template("ss-server -s $HOST -p $PORT -l $LOCAL_PORT -k $PASSWORD -m $METHOD -t $TIMEOUT -u --fast-open &").substitute(
            HOST = HOST_IP,
            PORT = str(port),
            LOCAL_PORT = str(self.local_port),
            PASSWORD = password,
            METHOD = method,
            TIMEOUT = str(timeout)
        )

        def _exec(content,out_file):
            pid = self.execCommand(content,out_file)
            return pid

        # mkdir -p, ensure the directory exists
        self.execOut("mkdir -p "+self.get_file_directory()+"/log/")
        LOG_FILE = self.get_file_directory()+"/log/"+"port_"+str(port)+".log"
        file_log = open(LOG_FILE,'w',1)

        #f = Process(target=_exec,args=(cmd_content,file_log))
        #f.start()
        _exec(cmd_content,file_log)
        # get the exact pid
        pid_arr = self.checkProcess()
        for item in pid_arr:
            if str(item['port']) == str(port):
                return item['pid']
        return False

    def killProcess(self,pid):
        try:
            os.kill(int(pid),0)
        except OSError:
            print "[LOG] no such process!"
            return False
        else:
            #check again if the process name is called "ss-server"
            pname = self.execOut("ps -p "+str(pid)+" -o comm=")
            if pname.split("\n")[0] == self.NAME:
                os.kill(int(pid),signal.SIGTERM)
            else:
                print "[OUT] wrong PID"

class ssServerDatabase:
    # server instance management for shadowsocks server instances.
    # @param `env` specify the running environment
    # for tests, `env` = "test",
    # and for actual development, `env` = "normal"
    def __init__(self,env="normal"):

        # directory for storing database data
        self.db_dir = self.get_file_directory()+"/data/"

        if env == "normal":
            self.db_name = "ss_server.db"
        elif env == "test":
            self.db_name = "ss_server_test.db"

        self.env = env
        self.timezone = 0
        # ensure the directory exists
        self.execOut("mkdir -p "+self.db_dir)
        conn = sqlite3.connect(self.db_dir+self.db_name)

        self.connection = conn
        self.cursor     = conn.cursor()

        # create ss_server table by default
        self.createTable()
        pass

    def get_file_directory(self):
        full_path = os.path.realpath(__file__)
        path,file = os.path.split(full_path)
        return path

    def execOut(self,cmd):
        p = subprocess.Popen(cmd,shell=True, stdout= subprocess.PIPE)
        (out,err) = p.communicate()
        return out

    def open(self):
        return sqlite3.connect(self.db_dir+self.db_name)

    def close(self):
        if self.connection != None:
            self.connection.close()

    def deleteTestDatabase(self):
        if self.env == "test":
            try:
                if os.path.exists(self.db_dir+self.db_name):
                    os.remove(self.db_dir+self.db_name)
                    return True
            except Exception as e:
                traceback.print_exc()
                return None

    def createTable(self):
        # ss database table
        # NOTICE: start_time & expire_time are ALL UTC TIME !!!!!!!!!!!!!!
        try:
            table_str = '''CREATE TABLE IF NOT EXISTS ss_server(
            ssid text unique,
            start_time datetime,
            expire_time datetime,
            uid text,
            server_port text,
            server_pid text,
            password text,
            method text,
            type text,
            status text
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
    # uid         : user id
    # ssid        : shadowsocks id
    # avail_days  : server instance availabale days (of course it depends on how much the user had paid for)
    # server_port : server_port for shadowscoks (once created, it cann't be modified by user)
    # server_pid  : pid for this instance
    # password    : password for shadowsocks (can be modified by user)
    # method      : crypt method for shadowsocks (can be modified by user)
    # type        : reserved for future usages (CHANGABLE | STABLE)
    # status      : server instance status (ACTIVE | HALT)
    def insertServerInstance(self,ssid,uid,avail_days,server_port,server_pid,password,method,s_type):
        try:
            insert_str = "INSERT INTO ss_server VALUES(?,?,?,?,?,?,?,?,?,?)"
            _STATUS  = "ACTIVE"
            # WARNING : timezone!!!!!
            curr_timestamp = timeUtil.getCurrentUTCtimestamp()
            expire_timestamp = curr_timestamp + int(float(avail_days)) * 24 * 3600

            start_time = timeUtil.getReadableTime(curr_timestamp,0) #UTC
            expire_time = timeUtil.getReadableTime(expire_timestamp,0) # UTC

            cursor = self.cursor
            cursor.execute(insert_str,(str(ssid),start_time,expire_time,str(uid),str(server_port),str(server_pid),str(password),str(method),str(s_type),_STATUS))
            self.connection.commit()
            return True
        except Exception as e:
            traceback.print_exc()
            return False
        pass

    # just for debugging==========
    def _readRawData(self):
        select_str = "SELECT * FROM ss_server"
        c = self.cursor
        data = c.execute(select_str)
        for row in data:
            print row

    def updateMethod(self,ssid,method):
        try:
            _str = "UPDATE ss_server SET method = ? WHERE ssid = ?"
            c = self.cursor
            c.execute(_str,(method,str(ssid)))
            self.connection.commit()
            return True
        except:
            traceback.print_exc()
            return False
        pass

    def updatePassword(self,ssid,password):
        try:
            _str = "UPDATE ss_server SET password = ? WHERE ssid = ?"
            c = self.cursor
            c.execute(_str,(password,str(ssid)))
            self.connection.commit()
        except:
            traceback.print_exc()
            return False
        pass

    def getItem(self,ssid):
        _item = {}
        try:
            c = self.cursor
            _str = "SELECT * FROM ss_server WHERE `ssid` = ?"
            data = c.execute(_str,[str(ssid)])
            _data = c.fetchone()

            if _data == None:
                return None
            else:
                _item["ssid"] = _data[0]
                _item["start_time"] = _data[1]
                _item["expire_time"] = _data[2]
                _item["uid"] = _data[3]
                _item["server_port"] = _data[4]
                _item["server_pid"] = _data[5]
                _item["password"] = _data[6]
                _item["method"] = _data[7]
                _item["type"] = _data[8]
                _item["status"] = _data[9]
                return _item
        except:
            return False
        pass

    def postponeExpireDate(self,ssid,postpone_days):
        try:
            # first read expire_date
            c = self.cursor
            _str = "SELECT expire_time FROM ss_server WHERE `ssid` = ?"

            data = c.execute(_str,[str(ssid)])
            _date = c.fetchone()
            if _date == None:
                return False
            else:
                _dd = _date[0]
                #get UTC timestamp
                _timestamp = timeUtil.getUTCtimestamp(_dd,0)

                _new_date = timeUtil.getReadableTime(int(float(postpone_days)) * 24 * 3600 + _timestamp,0)
                update_str = "UPDATE ss_server SET expire_time = ? WHERE ssid = ?"
                c.execute(update_str,(_new_date,str(ssid)))
                self.connection.commit()
        except Exception as e:
            traceback.print_exc()
            return False
        pass

    def changeInstanceStatus(self,ssid,status):
        try:
            c = self.cursor
            update_str = "UPDATE ss_server SET status = ? WHERE ssid = ?"
            if status == "ACTIVE" or status == "HALT":
                c.execute(update_str,(status,str(ssid)))
                self.connection.commit()
            else:
                return False
        except:
            traceback.print_exc()
            return False

    def deleteInstance(self,ssid):
        try:
            c = self.cursor
            delete_str = "DELETE FROM ss_server WHERE ssid = ?"
            c.execute(delete_str,[str(ssid)])
            self.connection.commit()
        except:
            traceback.print_exc()
            return False
            pass

    def checkExpiredInstance(self):
        model_arr = []
        try:
            c = self.cursor
            # datetime('now') returns UTC time
            sort_str = "SELECT * FROM ss_server WHERE expire_time < datetime('now') and status = 'ACTIVE' ORDER BY expire_time DESC"

            data = c.execute(sort_str)

            for row in data:
                model = {
                    "port" : 0,
                    "ssid" : 0
                }
                model["port"] = row[4]
                model["ssid"] = row[0]
                model_arr.append(model)
            return model_arr
        except Exception as e:
            traceback.print_exc()
            return []
        pass
    # get all instances that is active
    def getActiveInstances(self):
        model_arr = []
        try:
            c = self.cursor
            ins_str = "SELECT * from ss_server WHERE status = 'ACTIVE'"

            data = c.execute(ins_str)

            for row in data:
                model = {
                    "port" : 0,
                    "ssid" : 0
                }
                model["port"] = row[4]
                model["ssid"] = row[0]
                model_arr.append(model)
            return model_arr
        except Exception as e:
            traceback.print_exc()
            return []
        pass

def controlInstance(ssid,op):
    db = ssServerDatabase()
    proc = ssProcess()
    item = db.getItem(str(ssid))

    if op == "ACTIVE":
        proc.createProcess(item["server_port"],item["password"],method=item["method"])
    elif op == "HALT":
        try:
            # get pid of an instance
            pids = proc.checkProcess(port=item["server_port"])
            if len(pids) == 0:
                return False
            else:
                proc.killProcess(pids[0]["pid"])
        except Exception as e:
            traceback.print_exc()
            return False
    else:
        return False
