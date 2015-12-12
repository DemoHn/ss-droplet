__author__ = 'Mingchuan'
from apscheduler.schedulers.background import BackgroundScheduler
from model.db_service import serviceInfo
import time
from datetime import datetime
from config import config
from core.revoke import revoke
from core.socket import send_socket_request
import json

# cron task
# That means, the following function will be executed periodically and, of course, in schedule.
"""
This function is dedicated for checking if one instance is expired.
If so, this instance should be suddenly shutdown and notify the main server to change the status
and write the log
"""
def send_heart_beat_package():
    infoDB = serviceInfo()
    idfs = infoDB.checkExpiredService()
    idfs_info = []
    # revoke expired service
    if idfs["status"] == "success":
        idfs_info = idfs["info"]
        for item in idfs_info:
            revoke(item)
            time.sleep(0.2)

    pack_json = {
        "command":"heart_beat",
        "kill_idfs":idfs_info
    }
    # send heart_beat package
    if config["CONTROL_SERVER_IP"] != "":
        send_socket_request(
            config["CONTROL_SERVER_IP"],
            config["CONTROL_SERVER_UDP_PORT"],
            json.dumps(pack_json),
            type="UDP"
        )

def start_cron_task():
    scheduler = BackgroundScheduler()

    # add job with some rules
    # 1. send a heart_beat UDP package to declare that the server is still alive.
    #    As for the frequency... 0s or 30s per every miniute
    scheduler.add_job(send_heart_beat_package,'cron',second="*/30")
    # start the scheudler
    scheduler.start()
    return scheduler

def stop_cron_task(scheduler):
    scheduler.shutdown()

