#! /usr/bin/env python
# encoding:utf-8

import sys,os
import subprocess
import json
dir = os.getcwd()
sys.path.append(dir)
from core.socket import start_socket_server, send_socket_request
from cron_task import start_cron_task, stop_cron_task
from config import config
from model.db_ss_server import ssServerDatabase
from model.db_service import serviceInfo
import time

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

    start_socket_server()
    print("start web listening port: "+str(config["SERVER_LISTEN_PORT"]))

    scheduler = start_cron_task()
    try:
        while True:
            time.sleep(1)
    # if the server received KILL signal, just exit
    except (KeyboardInterrupt,SystemExit):
        stop_cron_task(scheduler)

# for the first time, do the function
def system_init():
    lock_file_exists = os.path.exists(get_file_directory()+"/.init.lock")

    if lock_file_exists == False:
        init()
    else:
        send_pack = {
            "command": "register_server",
            "info":{
                "listen_port":config["SERVER_LISTEN_PORT"],
                "location":config["SERVER_LOCATION"],
                "service_quota":config["SERVICE_QUOTA"]
            }
        }
        # send
        for i in range(0,3):
            return_data = send_socket_request(
                config["CONTROL_SERVER_IP"],
                config["CONTROL_SERVER_TCP_PORT"],
                json.dumps(send_pack),
                type="TCP"
            )

            if return_data["status"] == "success":
                break
            else:
                time.sleep(1)
        # initialize database
        ssServerDatabase()
        serviceInfo()
        # remove the lock
        os.remove(get_file_directory()+"/.init.lock")
        init()
    pass

system_init()
