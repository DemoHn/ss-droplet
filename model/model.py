__author__ = 'Mingchuan'
import redis
import os,subprocess,traceback
import sqlite3
from config import config
import cymysql
class Database:
    instance = None
    def __init__(self,env="normal"):
        # server instance management for shadowsocks server instances.
        # @param `env` specify the running environment
        # for tests, `env` = "test",
        # and for actual development, `env` = "normal"
        self.db_dir = ""
        self.env    = env
        try:
            # create new connection
            conn = cymysql.connect(
                host   = config["MYSQL_CONNECTION_IP"],
                user   = config["MYSQL_USER"],
                passwd = config["MYSQL_PASSWORD"],
                charset= "utf8"
            )
            self.connection = conn
            self.cursor     = conn.cursor()
            if env == "normal":
                self.db_name = "ss_subnode"
            elif env == "test":
                self.db_name = "ss_subnode_test"
            # create database
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS "+self.db_name)
            self.cursor.execute("USE "+self.db_name)
        except Exception as e:
            traceback.print_exc()

    @staticmethod
    def get_instance(env = "normal"):
        if Database.instance is None:
            Database.instance = Database(env=env)
        return Database.instance

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
        # USE mariaDB
        if self.env == "test":
            try:
                c = self.cursor
                c.execute("DROP DATABASE "+self.db_name)
                c.execute("CREATE DATABASE "+self.db_name)
                c.execute("USE DATABASE "+self.db_name)
            except Exception as e:
                traceback.print_exc()

# TODO add redis server
# Redis Server. Need redis support on server side
# To install redis , just prompt:
# $ apt-get install redis-server
# $ pip3 install redis
class RedisDatabase:
    def __init__(self,env="normal"):
        self.redis = self.connect()
        pass

    def connect(self):
        try:
            r = redis.StrictRedis(host=config["REDIS_HOST"], port=config["REDIS_PORT"], db=0)
            # test if redis server is connected
            r.ping()
            return r
        except Exception as e:
            return None
