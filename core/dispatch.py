#coding=utf-8
__author__ = 'Mingchuan'
from config import config
from model.db_service import serviceInfo
from utils import returnModel
from random import randint
import time
# Last Edit : 2015-12-5
# create new instance for service
# @params
# max_traffic : max traffic allowed
# max_devices : max devices allowed
# type        : instance type (only SHADOWSOCKS is available till now)
# expire_timestamp : expire time of this service(UTC). After that time, the instance will revoke automatically
def new_service(max_traffic,max_devices,type,expire_timestamp):
    # first get active service nums
    sDB = serviceInfo()
    rtn = returnModel()
    count_res = sDB.countActiveService()

    # set max num
    if max_traffic == -1 or max_traffic >= config["MMAX_TRAFFIC"]:
        max_traffic = config["MMAX_TRAFFIC"]
    if max_devices == -1 or max_traffic >= config["MMAX_DEVICES"]:
        max_devices - config["MMAX_DEVICES"]

    if count_res == None:
        return rtn.error(420)
    else:
        active_num = int(count_res["info"])
        # if out of quota
        if active_num >= config["SERVICE_QUOTA"]:
            return rtn.error(421)
        else:
            if type == "shadowsocks":
                result = start_shadowsocks()
                if result["status"] == "error":
                    return rtn.error(result['code'])
                elif result['status'] == "success":
                    # add service info
                    service_idf = result["info"]
                    sDB.createNewService(service_idf,max_devices,max_traffic,expire_timestamp,type)
                    return rtn.success(result['info'])
                else:
                    return rtn.error(420)
            else:
                return rtn.error(405)
    pass

def gen_service_idf():
    loop_str = "0123456789aWcdeFEhijklmnopQrstuvwSyzZ"
    time_int = (int(time.time()*1000) % (1000*1000)) + int(randint(100,999) * (1000*1000))
    a = []
    while time_int > 0:
        a.append(loop_str[int(time_int) % 36])
        time_int = int(time_int / 36)
    a.reverse()
    return ''.join(a)

def start_shadowsocks():

    return_data_config = {
        "server_port" : "",
        "password"    : "",
        "method"      : "",
        "timeout"     : ""
    }

    return_data = {
        "service_idf":"",
        "config":return_data_config
    }
    rtn = returnModel()
    from model.db_ss_server import ssServerDatabase
    from proc.proc_ss import ssProcess
    ssDB = ssServerDatabase()
    ssProc = ssProcess()
    port = 0
    # lock: to prevent infinite loop (for any reason)
    lock = 20
    while lock > 0:
        lock -= 1
        rand_port = randint(config["SHADOWSOCKS_MIN_PORT"],config["SHADOWSOCKS_MAX_PORT"])
        if ssDB.portCollision(int(rand_port)) == False:
            port = rand_port
            break
    if port == 0:
        return rtn.error(422)
    else:
        # first generate params
        service_idf  = gen_service_idf()
        service_port = port
        service_password = str(randint(1000,9999)) + str(randint(1000,9999))
        service_method = config["SS_DEFAULT_METHOD"]
        service_timeout = config["SS_DEFAULT_TIMEOUT"]

        res = ssDB.insertServerInstance(service_idf,service_port
                                        ,service_password,service_method,service_timeout)
        if res == None:
            return rtn.error(423)
        elif res["status"] == "error":
            return rtn.error(423)
        elif res["status"] == "success":
            # insert success, then create real process
            result = ssProc.createProcess(service_port,service_password,service_timeout,service_method)
            # if the process not open successfully (maybe... just not install ss-server LOL)
            # (2015-12-06)UPDATE : DO NOT CHECK THE RESULT OF PROCESS CREATION!!

            # insert config data
            return_data_config["server_port"] = service_port
            return_data_config["password"]    = service_password
            return_data_config["method"]      = service_method
            return_data_config["timeout"]     = service_timeout
            return_data["service_idf"]        = service_idf
            return rtn.success(return_data)
    pass
