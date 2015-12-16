__author__ = 'Nigshoxiz'
# Last Edit: 2015-12-10
from config import config
from model.db_service import serviceInfo
from utils import returnModel, timeUtil
from config import config
# function `postpone`
# If user wants to use the same service for a longer time,
# then just modify its expire_timestamp
def postpone(service_idf,postpone_timestamp):
    rtn  = returnModel()
    siDB = serviceInfo()
    p_time = int(postpone_timestamp)
    postpone_result = siDB.updateExpireTimestamp(service_idf,p_time)

    if postpone_result == None:
        return rtn.error(500)
    elif postpone_result["status"] == "success":
        return rtn.success(200)
    else:
        return rtn.error(postpone_result["code"])

def increase_traffic(service_idf,add_traffic):
    rtn  = returnModel()
    siDB = serviceInfo()
    add_result = siDB.increaseTraffic(service_idf,add_traffic)

    if add_result == None:
        return rtn.error(500)
    elif add_result["status"] == "success":
        return rtn.success(200)
    else:
        return rtn.error(add_result["code"])

def decrease_traffic(service_idf,add_traffic):
    rtn  = returnModel()
    siDB = serviceInfo()
    add_result = siDB.increaseTraffic(service_idf,add_traffic)

    if add_result == None:
        return rtn.error(500)
    elif add_result["status"] == "success":
        return rtn.success(200)
    else:
        return rtn.error(add_result["code"])
