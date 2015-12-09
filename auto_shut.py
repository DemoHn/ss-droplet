from model.db_service import serviceInfo
import time
import threading
from config import config
from core.revoke import revoke
from core.socket import send_socket_request
import json
"""
This script is dedicated for checking if one instance is expired.
If so, this instance should be suddenly shutdown and notify the main server to change the status
and write the log
"""
def checkInstance():
    infoDB = serviceInfo()
    idfs = infoDB.checkExpiredService()
    idfs_info = []
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
    send_socket_request(
        config["CONTROL_SERVER_IP"],
        config["CONTROL_SERVER_UDP_PORT"],
        json.dumps(pack_json),
        type="UDP"
    )
    timer_init()

def timer_init():
    t = threading.Timer
    t(int(config["HEARTBEAT_PULSE"]),checkInstance).start()