__author__ = 'Mingchuan'
from apscheduler.schedulers.background import BackgroundScheduler
import time

# import databases
from model.db_service import serviceInfo
from model.db_traffic import serviceTraffic
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
    infoDB    = serviceInfo()
    trafficDB = serviceTraffic()

    idfs = infoDB.checkExpiredService()
    exceed = trafficDB.getExceedTrafficService()

    exceed_info = []
    idfs_info   = []

    # update traffic of all services
    update_traffic()

    print("kill")
    print(idfs)
    print("kill exceed")
    print(exceed)

    if idfs["status"] == "success":
        idfs_info = idfs["info"]
        for item in idfs_info:
            revoke(item)

    if exceed["status"] == 'success':
        exceed_info = exceed["info"]
        for item in exceed_info:
            revoke(item)

   # send heart_beat package
    pack_json = {
        "command":"heart_beat",
        "expire_idfs":idfs_info,
        "traffic_exceed_idfs":exceed_info
    }

    if config["CONTROL_SERVER_IP"] != "": #and config["SEND_HEARTBEAT_PACK"] == True:
        send_socket_request(
            config["CONTROL_SERVER_IP"],
            config["CONTROL_SERVER_UDP_PORT"],
            json.dumps(pack_json),
            type="UDP"
        )

def reset_traffic(strategy_name):
    def split_traffic_strategy(strategy_str):
        # remove spaces
        strategy_str = strategy_str.replace(" ","")
        return strategy_str.split(",")

    trafficDB = serviceTraffic()
    servDB    = serviceInfo()
    result    = trafficDB.getTrafficInstancesByStrategy(strategy_name)
    if result == None:
        return None
    elif result["status"] == "error":
        return None
    else:
        traffic_arr = result["info"]
        for item in traffic_arr:
            s_str = item["service_strategy"]
            s_idf = item["service_idf"]
            stgy_arr = split_traffic_strategy(s_str)

            new_traffic = float(stgy_arr[1])
            # total traffic reset to maximum
            servDB.resetTraffic(s_idf,new_traffic)
            # reset zero for this service
            trafficDB.resetZero(s_idf)

def update_traffic():
    servDB    = serviceInfo()
    print(servDB)
    trafficDB = serviceTraffic()
    item_result = servDB.getItems()
    if item_result == None:
        return None
    elif item_result["status"] == "error":
        return None
    else:
        # get all items
        items = item_result["info"]
        print(items)
        for item in items:
            serv_type = item["service_type"]
            serv_idf  = item["service_idf"]
            # TODO 暂时只对使用shadowsocks-obfs的服务进行流量更新
            if serv_type == "shadowsocks-obfs":
                from model.db_ss_obfs_server import ssOBFSServerDatabase
                from proc.proc_ss import ssOBFS_Process
                ssProc = ssOBFS_Process()
                ssDB   = ssOBFSServerDatabase()

                # get service listen port
                port_result = ssDB.getItem(serv_idf)
                if port_result != None:
                    if port_result["status"] == "success":
                        port = int(port_result["info"]["server_port"])
                        # get traffic
                        t_info = ssProc.getTraffic(port)
                        # change to MBs
                        u_t    = round(float(t_info["upload"]) / (1000 * 1000),1)
                        d_t    = round(float(t_info["download"]) / (1000 * 1000),1)

                        trafficDB.updateTraffic(serv_idf,u_t,d_t)

def reset_traffic_per_month():
    reset_traffic("AccountPerMonthStrategy")

def reset_traffic_per_day():
    reset_traffic("AccountPerDayStrategy")

def start_cron_task():
    """
    scheduler = BackgroundScheduler()

    # add job with some rules
    # 1. send a heart_beat UDP package to declare that the server is still alive.
    #    As for the frequency... 0s or 30s per every miniute
    scheduler.add_job(send_heart_beat_package,'cron',second="*/5")

    # 2. reset traffic
    scheduler.add_job(reset_traffic_per_day,'cron',hour="0",minute="0",second="0")
    scheduler.add_job(reset_traffic_per_month,'cron',day="1",hour="0",minute="0",second="0")

    # start the scheduler
    scheduler.start()
    return scheduler
    """
    while True:
        send_heart_beat_package()
        time.sleep(5)
def stop_cron_task(scheduler):
    scheduler.shutdown()
