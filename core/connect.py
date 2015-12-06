__author__ = 'Mingchuan'
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
        print(info)
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
                if res["status"] == "error":
                    return rtn.error(res["code"])
                else:
                    conf_return_model['info'] = res['info']
            else:
                return rtn.error(405)
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
