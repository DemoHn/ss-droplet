import sys,os,re
import subprocess
import threading
import urllib2
from ss_server import ssProcess, ssServerDatabase, controlInstance,timeUtil
import requests
from string import Template
from config import config

import traceback
"""
This script is worked for checking if one instance is expired.
If so, this instance should be suddenly shutdown and notify the main server to change the status
and write the log
"""
def checkInstance():
    db = ssServerDatabase()
    proc = ssProcess()
    eis = db.checkExpiredInstance()
    halt_arr = []
    # halt them
    for item in eis:
        # first
        db.changeInstanceStatus(item["ssid"],"HALT")
        controlInstance(item["ssid"],"HALT")
        halt_arr.append(str(item["ssid"]))
        print "[LOG] kill SSID : "+item["ssid"]+" PORT:"+item["port"] +" at UTC"+timeUtil.getReadableTime(timeUtil.getCurrentUTCtimestamp(),0)
    pass

    send_heart_beat_request(halt_arr)
    timer_init()

def timer_init():
    t = threading.Timer
    t(25,checkInstance).start()
def send_heart_beat_request(halt_ssid_arr):
    ssid_str = "W".join(halt_ssid_arr)

    rtn_payload = {
        "timestamp":0, # UTC TIME !!!!!!!!!!
        "halt":ssid_str #halt ssid array
    }

    rtn_payload["timestamp"] = timeUtil.getCurrentUTCtimestamp()
    url = Template("http://$SERVER_IP:$SERVER_PORT/api/listen/heart_beat").substitute(
        SERVER_IP=config["CONTROL_SERVER_IP"],
        SERVER_PORT=config["CONTROL_SERVER_PORT"]
    )
    try:
        r = requests.post(url,data = rtn_payload)
    except Exception as e:
        traceback.print_exc()
        return None
    pass
