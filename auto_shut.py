from model.db_service import serviceInfo
import time
import threading
from config import config
from utils import timeUtil
from core.revoke import revoke
import traceback
"""
This script is dedicated for checking if one instance is expired.
If so, this instance should be suddenly shutdown and notify the main server to change the status
and write the log
"""
def checkInstance():
    infoDB = serviceInfo()
    idfs = infoDB.checkExpiredService()
    if idfs["status"] == "success":
        for item in idfs["info"]:
            revoke(item)
            time.sleep(0.2)
    pass
    timer_init()

def timer_init():
    t = threading.Timer
    t(config["HEARTBEAT_PULSE"],checkInstance).start()