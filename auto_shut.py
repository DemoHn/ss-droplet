from model.db_service import serviceInfo
import subprocess
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

    pass
    timer_init()

def timer_init():
    t = threading.Timer
    t(config["HEARTBEAT_PULSE"],checkInstance).start()