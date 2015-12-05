import sys,os,re
import subprocess
import threading
import requests
from string import Template
from config import config
from utils import timeUtil
import traceback
"""
This script is worked for checking if one instance is expired.
If so, this instance should be suddenly shutdown and notify the main server to change the status
and write the log
"""
def checkInstance():
    pass
    timer_init()

def timer_init():
    t = threading.Timer
    t(config["HEARTBEAT_PULSE"],checkInstance).start()