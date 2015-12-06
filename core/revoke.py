__author__ = 'Mingchuan'

from config import config
from utils import returnModel
from model.db_service import serviceInfo
from model.redis_device import redisDevice
# delete all information about this server
def revoke(service_idf):
    rtn  = returnModel()
    inDB = serviceInfo()
    rDB  = redisDevice(service_idf)
    # first get item
    item_result = inDB.getItem(service_idf)

    if item_result == None:
        return rtn.error(500)
    elif item_result["status"] == "error":
        return rtn.error(item_result["code"])
    else:
        info = item_result["info"]
        # delete server instance in the database and halt the process
        service_type = info["service_type"]

        if service_type == "shadowsocks":
            res = halt_shadowsocks_service(service_idf)
            if res["status"] == "success":
                result = inDB.deleteItem(service_idf)
                rDB.deleteSet()
                if result["status"] == "success":
                    return rtn.success(200)
                else:
                    return result
                # delete info in serviceInfo
            else:
                return res
    pass

def halt_shadowsocks_service(service_idf):
    rtn = returnModel()
    from model.db_ss_server import ssServerDatabase
    from proc.proc_ss import ssProcess
    ssDB = ssServerDatabase()
    ssProc = ssProcess()
    item = ssDB.getItem(service_idf)

    if item == None:
        return rtn.error(500)
    elif item["status"] == "error":
        return rtn.error(item["code"])
    else:
        port = int(item["info"]["server_port"])
        kill_proc = ssProc.checkProcess(port=port)
        # can not find pid in the system
        if len(kill_proc) == 0:
            return rtn.error(450)
        else:
            _pid = kill_proc[0]["pid"]
            result = ssProc.killProcess(_pid)
            if result == False:
                return rtn.error(450)
            else:
                # kill record in database
                ssDB.deleteInstance(service_idf)
                return rtn.success(200)
    pass