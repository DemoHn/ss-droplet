#coding=utf-8
__author__ = 'Nigshoxiz'
from config import config
from model.db_service import serviceInfo
from utils import returnModel
from random import randint
import time
# Last Edit : 2015-12-13
# create new instance for service
# @params
# max_traffic : max traffic allowed
# max_devices : max devices allowed
# type        : instance type (only SHADOWSOCKS is available till now)
# expire_timestamp : expire time of this service(UTC). After that time, the instance will revoke automatically
def new_service(max_traffic,max_devices,type,expire_timestamp,strategy=""):
    # first get active service nums
    sDB = serviceInfo()
    rtn = returnModel()
    count_res = sDB.countActiveService()

    # set max num
    if max_traffic == -1 or max_traffic >= config["MMAX_TRAFFIC"]:
        max_traffic = config["MMAX_TRAFFIC"]
    if max_devices == -1 or max_traffic >= config["MMAX_DEVICES"]:
        max_devices = config["MMAX_DEVICES"]

    if count_res == None:
        return rtn.error(420)
    else:
        active_num = int(count_res["info"])
        # if out of quota
        if active_num >= config["SERVICE_QUOTA"]:
            return rtn.error(421)
        else:
            # service type switch
            if type == "shadowsocks":
                result = start_shadowsocks()
            elif type == "shadowsocks-obfs":
                result = start_shadowsocks_obfs(strategy)
            else:
                return rtn.error(405)
            # handle callback
            if result["status"] == "error":
                return rtn.error(result['code'])
            elif result['status'] == "success":
                # add service info
                service_idf = result["info"]["service_idf"]
                sDB.createNewService(service_idf,max_devices,max_traffic,expire_timestamp,type)
                return rtn.success(result['info'])
            else:
                return rtn.error(420)

def gen_service_idf(length=16):
    loop_str = "0123456789aWcdeFEhijklmnopQrstuvwSyzZBRrq"
    a = []
    for i in range(0,length):
        s = loop_str[randint(0,len(loop_str)-1)]
        a.append(s)
    return ''.join(a)

def gen_password(length):
    length = int(length)
    str_dict = ("ABVDEXGHIJ","KLMZOPQRUT","0123456789","abudefghzj","klmnopqwst","0123456789","0123456789","!@?&{}[|])")

    passwd_arr = []
    for i in range(0,length):
        dict_index = randint(0,7)
        str_index  = randint(0,9)
        passwd_arr.append(str_dict[dict_index][str_index])

    return "".join(passwd_arr)

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
        service_password = gen_password(16)
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

def start_shadowsocks_obfs(traffic_strategy):
    return_data = {
        "service_idf":"",
        "config":""
    }
    rtn = returnModel()
    from model.db_ss_obfs_server import ssOBFSServerDatabase
    from model.db_traffic import serviceTraffic
    from proc.proc_ss import ssOBFS_Process
    ssDB = ssOBFSServerDatabase()
    ssProc = ssOBFS_Process()
    ssT    = serviceTraffic()
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
        passwd = gen_password(16)
        res    = ssDB.insertServerInstance(service_idf,port,passwd)

        if res == None:
            return rtn.error(423)
        elif res["status"] == "error":
            return rtn.error(423)
        elif res["status"] == "success":
            result = ssProc.createServer(port,passwd)
            ssT.createNewTraffic(service_idf,traffic_strategy)
            if result == True:
                return_data["service_idf"] = service_idf
                return_data["config"]      = ssProc.generateLocalConfig(port,passwd)
                return rtn.success(return_data)
            else:
                return rtn.error(1200)
    pass