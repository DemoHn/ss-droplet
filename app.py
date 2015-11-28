#! /usr/bin/env python
# encoding:utf-8

import sys,os
import subprocess
import time
from multiprocessing import Process
import traceback
from datetime import datetime
import requests
dir = os.getcwd()
sys.path.append(dir)

from web_control import listenOrder
from ss_server import ssProcess, ssServerDatabase, controlInstance
from auto_shut import checkInstance
from config import config
from string import Template

def get_file_directory():
    full_path = os.path.realpath(__file__)
    path,file = os.path.split(full_path)
    return path

def execCommand(cmd):
    p = subprocess.Popen(cmd,shell=True,stdout = subprocess.PIPE)
    (out,err) = p.communicate()
    return out

# check if some instances that are not open while it was marked as "active" in the database
# (usually when the server is going to restart)
def init():
    db = ssServerDatabase()
    ins = db.getActiveInstances()

    for row in ins:
        controlInstance(row["ssid"],"ACTIVE")

    f = Process(target=listenOrder)
    f.start()
    print "start web listening port: "+config["SERVER_LISTEN_PORT"]

    time.sleep(3)
    print "[LOG] start checking after 3 sec..."

    checkInstance()

    while True:
        time.sleep(1)

# for the first time, do the function
def system_init():
    lock_file_exists = os.path.exists(get_file_directory()+"/.init.lock")

    if lock_file_exists == False:
        init()
    else:
        # do some initiallzation works
        url_model = "http://$SERVER_IP:$PORT/api/add_server?quota=$QUOTA&listen_port=$LISTEN_PORT&key=$KEY&location=$LOCATION"

        url_str = Template(url_model).substitute(
            PORT = config["CONTROL_SERVER_PORT"],
            SERVER_IP = config["CONTROL_SERVER_IP"],
            QUOTA = config["SERVER_QUOTA"],
            LISTEN_PORT = config["SERVER_LISTEN_PORT"],
            KEY = config["SERVER_KEY"],
            LOCATION = config["SERVER_LOCATION"]
        )

        try:
            r = requests.get(url_str)
        except Exception as e:
            traceback.print_exc()

        # create database
        db = ssServerDatabase()
        ins = db.getActiveInstances()

        os.remove(get_file_directory()+"/.init.lock")
        init()
    pass

system_init()