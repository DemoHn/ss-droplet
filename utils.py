#coding=utf-8
__author__ = 'Mingchuan'
import os
import time
from datetime import datetime
import re
import json
from error_code import errcode

def get_file_directory():
    full_path = os.path.realpath(__file__)
    path,file = os.path.split(full_path)
    return path

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

# 统计本目录下所有*.py文件加在一起的总行数
def get_line_number(directory):
    num = 0
    # get file list
    file_list = os.listdir(directory)

    for item in file_list:
        _item = item
        item = os.path.normpath(directory+"/"+item)
        # if it is file and it is *.py
        if os.path.isfile(item) and item.find(".py") > 0 and item.find(".pyc") < 0 and item.find("bottle.py") < 0:
            f = open(item,"rb")
            nums = len(f.readlines())
            num += nums
            print("---"+str(_item)+": "+str(nums))
            f.close()
        elif os.path.isdir(item+"/") and _item != ".git" and _item != "assets" and _item != "lib":
            subdir = item

            num += get_line_number(subdir)
    return num
#行数统计
print("\nfinal line number: "+str(get_line_number(get_file_directory())))
