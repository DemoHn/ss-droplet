__author__ = 'Mingchuan'

import os,subprocess,traceback
import sqlite3
class Database:
    def __init__(self,env="normal"):
        # server instance management for shadowsocks server instances.
        # @param `env` specify the running environment
        # for tests, `env` = "test",
        # and for actual development, `env` = "normal"

        # directory for storing database data
        self.db_dir = self.get_file_directory()+"/../data/"
        self.env = env
        if env == "normal":
            self.db_name = "ss_server.db"
        elif env == "test":
            self.db_name = "ss_server_test.db"

        # ensure the directory exists
        self.execOut("mkdir -p "+self.db_dir)
        conn = sqlite3.connect(self.db_dir+self.db_name)

        self.connection = conn
        self.cursor     = conn.cursor()
        pass

    def get_file_directory(self):
        full_path = os.path.realpath(__file__)
        path,file = os.path.split(full_path)
        return path

    def get_app_root(self):
        return os.getcwd()

    def execOut(self,cmd):
        p = subprocess.Popen(cmd,shell=True, stdout= subprocess.PIPE)
        (out,err) = p.communicate()
        return out

    def deleteTestDatabase(self):
        if self.env == "test":
            try:
                if os.path.exists(self.db_dir+self.db_name):
                    os.remove(self.db_dir+self.db_name)
                    return True
            except Exception as e:
                traceback.print_exc()
                return None

# TODO add redis server
# Redis Server. Need redis support on server side
class RedisDatabase:
    def __init__(self):
        pass


