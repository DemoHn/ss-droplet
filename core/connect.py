__author__ = 'Nigshoxiz'
# Last Edit: 2015-12-6
from config import config
from model.db_service import serviceInfo
from model.redis_device import redisDevice
from utils import returnModel

# function `connect`
# when client ask connection to the remote server,
# the remote server should return configuration info and then
# client start to setup the tunnel in accordance to the configuration
def connect(service_idf,mac_addr):
    rtn  = returnModel()
    rd   = redisDevice(service_idf)
    siDB = serviceInfo()
    # first, find if service_idf can be found
    result = siDB.getItem(service_idf)
    if result == None:
        return rtn.error(500)
    elif result["status"] == "error":
        return rtn.error(430)
    else:
        info = result['info']
        # check if devices num is not full
        if (rd.countDevice()+int(rd.deviceInList(mac_addr))) > int(info["max_devices"]):
            return rtn.error(431)
        else:
            conf_return_model = {
                "service_type":"",
                "expire_time":"",
                "info":{}
            }
            # register device into device_db
            rd.newDevice(mac_addr)
            conf_return_model["expire_time"] = info["expire_time"]
            # get configuration
            if info["service_type"] == "shadowsocks":
                conf_return_model["service_type"] = "shadowsocks"
                res = get_shadowsocks_conf(service_idf)
            elif info["service_type"] == "shadowsocks-obfs":
                conf_return_model["service_type"] = "shadowsocks-obfs"
                res = get_shadowsocks_obfs_conf(service_idf)
            else:
                return rtn.error(405)

            if res["status"] == "error":
                return rtn.error(res["code"])
            else:
                conf_return_model['info'] = res['info']

            # get conf string then return
            return rtn.success(conf_return_model)
        pass

def get_shadowsocks_conf(service_idf):
    rtn = returnModel()
    from model.db_ss_server import ssServerDatabase
    ssDB = ssServerDatabase()
    item = ssDB.getItem(service_idf)
    if item == None:
        return rtn.error(500)
    elif item["status"] == "error":
        return rtn.error(item['code'])
    else:
        return rtn.success(item['info'])


def get_shadowsocks_obfs_conf(service_idf):
    rtn = returnModel()
    from model.db_ss_obfs_server import ssOBFSServerDatabase
    from proc.proc_ss import ssOBFS_Process
    ssOBFSProc = ssOBFS_Process()
    ssDB = ssOBFSServerDatabase()
    item = ssDB.getItem(service_idf)

    if item == None:
        return rtn.error(500)
    elif item["status"] == "error":
        return rtn.error(item['code'])
    else:
        port   = item["info"]["server_port"]
        passwd = item["info"]["password"]
        conf   = ssOBFSProc.generateLocalConfig(port,passwd)
        return rtn.success(conf)
