__author__ = 'Mingchuan'

import time
from datetime import datetime
import re
import json
from error_code import errcode

class timeUtil:
    def __init__(self):
        pass

    @staticmethod
    def getCurrentUTCtimestamp():
        # get timestamp
        # time.timezone represents for the seconds that current timestamp delayed
        return int(time.time()) + int(time.timezone)

    @staticmethod
    def getReadableTime(utc_timestamp,timezone):
        # final string e.g: 2015-10-12 17:39
        # here, timezone means hours before UTC
        # e.g: CST <--> +8
        _timestamp = int(utc_timestamp) + int(timezone)*3600

        return datetime.fromtimestamp(_timestamp).strftime("%Y-%m-%d %H:%M:%s")

    @staticmethod
    def getUTCtimestamp(readable_time,timezone):
        # here, timezone means hours before UTC
        # e.g: CST <--> +8
        re_str = "([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+)"
        m = re.search(re_str,readable_time)

        if m == None:
            return False
        else:
            year   = m.group(1)
            month  = m.group(2)
            date   = m.group(3)
            hour   = m.group(4)
            minute = m.group(5)

            dm     = datetime(int(year),int(month),int(date),int(hour),int(minute))
            tm     = time.mktime(dm.timetuple())
            return int(tm) - timezone * 3600

class returnModel:
    def __init__(self,type="json"):
        self.rtn_type = type
        pass

    def success(self,info,code=200,type="json"):
        rtn = {
            "status":"success",
            "code" :code,
            "info" : info
        }

        if self.rtn_type == "string":
            return json.dumps(rtn)
        else:
            return rtn

    def error(self,error_code,info="",type="json"):
        rtn = {
            "status":"error",
            "code" :error_code,
            "info" : ""
        }

        if info != "":
            rtn["info"] = info
        else:
            try:
                rtn["info"] = errcode[str(error_code)]
            except Exception as e:
                rtn["info"] = "unknown error description"

        if self.rtn_type == "string":
            return json.dumps(rtn)
        else:
            return rtn
