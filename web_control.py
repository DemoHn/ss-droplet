# coding=utf-8

from bottle import run,route,request
import os,sys,re
from multiprocessing import Process
from ss_server import ssProcess, ssServerDatabase, controlInstance
import json
import traceback
from config import config
# listen orders from control server
# (for controling instances of this server)

dir = os.getcwd()
sys.path.append(dir)

from config import config
controlIP = config["CONTROL_SERVER_IP"]

@route('/control',method="POST")
def route_index():
    """
    # @params
    # order : create | update | delay | cgstatus | delete

    (1) create
    create a new instance and leave a record in the database
    ssid        : instance id
    uid         : user id
    delay_days  : delay days
    server_port : server port
    method      : shadowsocks encrypt method
    password    : shadowsocks password
    timeout     : timeout
    (2) update
    ssid :
    item : (password | method)
    new_value:

    (3) delay
    ssid :
    delay_days  :

    (4) cgstatus
    ssid  :
    status: (ACTIVE | HATT)

    (5) delete
    ssid :

    """
    f = request.forms
    origin_ip = request.environ.get("REMOTE_ADDR")

    err_info = {}
    # reject orders from other IP

    if origin_ip != controlIP:
        err_info = {}
        err_info['status'] = "error"
        err_info['info'] = "reject"

        return json.dumps(err_info)
    else:
        db  = ssServerDatabase()
        proc = ssProcess()

        if f.get("order") == "create":
            # first get data
            _password = f.get("password")

            if f.get("timeout") == None:
                _timeout = 100
            else:
                _timeout = f.get("timeout")

            _ssid = f.get("ssid")
            _uid  = f.get("uid")
            _server_port = f.get("server_port")
            _delay_days  = f.get("delay_days")

            if f.get("type") == None:
                _type = "STABLE"
            else:
                _type = f.get("type")
            if f.get("method") == None:
                _method = "rc4-md5"
            else:
                _method= f.get("method")

            # then create the process

            try:
                _pid = proc.createProcess(int(_server_port),_password,method=_method)
                # next write it to the database
                db.insertServerInstance(_ssid,_uid,_delay_days,_server_port,_pid,_password,_method,_type)
            except Exception as e:
                traceback.print_exc()
                # return error
                err_info['status'] = "error"
                err_info['info'] = "create instance error"
                return json.dumps(err_info)
            else:
                # read the data in the db (to get start_time)
                info = db.getItem(_ssid)
                if info == False:
                    err_info['status'] = "error"
                    err_info['info'] = "can't get item"
                    return json.dumps(err_info)
                else:
                    err_info['status'] = "success"
                    err_info['info']   = info
                    return json.dumps(err_info)
                pass
        elif f.get("order") == "update":
            _ssid = f.get("ssid")
            _item = f.get("item")
            _val  = f.get("new_value")

            # first get item
            ins = db.getItem(_ssid)

            if _item == "password":
                try:
                    # restart the process
                    proc.createProcess(ins["server_port"],_val,method=ins["method"])
                    # then update the db
                    db.updatePassword(_ssid,_val)
                except Exception as e:
                    traceback.print_exc()
                    err_info['status'] = "error"
                    err_info['info'] = "update error"
                    return json.dumps(err_info)
                else:
                    err_info['status'] = "success"
                    err_info['info']   = "update success"
                    return json.dumps(err_info)
            elif _item == "method":
                try:
                    # restart the process
                    proc.createProcess(ins["server_port"],ins["password"],method=_val)
                    # then update the db
                    db.updateMethod(_ssid,_val)
                except Exception as e:
                    traceback.print_exc()
                    err_info['status'] = "error"
                    err_info['info'] = "update error"
                    return json.dumps(err_info)
                else:
                    err_info['status'] = "success"
                    err_info['info']   = "update success"
                    return json.dumps(err_info)
            else:
                err_info['status'] = "error"
                err_info['info'] = "no such item!"
                return json.dumps(err_info)
            pass
        # 续费
        elif f.get("order") == "delay":
            _ssid = f.get("ssid")
            _days = f.get("delay_days")

            try:
                db.postponeExpireDate(_ssid,_days)
                # and active the instance without any hesitation
                db.changeInstanceStatus(_ssid,"ACTIVE")

                # if the instance has been halted , then acitve it
                controlInstance(_ssid,"ACTIVE")
            except Exception as e:
                err_info['status'] = "error"
                err_info['info'] = "update error"
                return json.dumps(err_info)
            else:
                err_info['status'] = "success"
                err_info['info']   = "update success"
                return json.dumps(err_info)
            pass

        elif f.get("order") == "cgstatus":
            _ssid = f.get("ssid")
            _status = f.get("status")

            if _status == "ACTIVE":
                try:
                    db.changeInstanceStatus(_ssid,"ACTIVE")
                    # active the process
                    controlInstance(_ssid,"ACTIVE")
                except Exception as e:
                    traceback.print_exc()
                    err_info['status'] = "error"
                    err_info['info'] = "update error"
                    return json.dumps(err_info)
                else:
                    err_info['status'] = "success"
                    err_info['info']   = "update success"
                    return json.dumps(err_info)
            elif _status == "HALT":
                try:
                    db.changeInstanceStatus(_ssid,"HALT")
                    # active the process
                    controlInstance(_ssid,"HALT")
                except Exception as e:
                    traceback.print_exc()
                    err_info['status'] = "error"
                    err_info['info'] = "update error"
                    return json.dumps(err_info)
                else:
                    err_info['status'] = "success"
                    err_info['info']   = "update success"
                    return json.dumps(err_info)
            else:
                err_info['status'] = "error"
                err_info['info'] = "no such item"
                return json.dumps(err_info)
            pass
        elif f.get("order") == "delete":
            _ssid = f.get("ssid")
            try:
                controlInstance(_ssid,"HALT")
                db.deleteInstance(_ssid)
            except Exception as e:
                traceback.print_exc()
                err_info['status'] = "error"
                err_info['info'] = "delete error"
                return json.dumps(err_info)
            else:
                err_info['status'] = "success"
                err_info['info'] = "delete success"
                return json.dumps(err_info)
            pass
        # read an item
        elif f.get("order") == "read":
            _ssid = f.get("ssid")
            info = {}
            try:
                info = db.getItem(_ssid)
            except Exception as e:
                traceback.print_exc()
                err_info['status'] = "error"
                err_info['info'] = "delete error"
                return json.dumps(err_info)
            else:
                err_info['status'] = "success"
                err_info['info'] = info
                return json.dumps(err_info)
            pass
        else:
            err_info['status'] = "error"
            err_info['info'] = "no such item"
            return json.dumps(err_info)
            pass

def listenOrder():
    PORT = config["SERVER_LISTEN_PORT"]
    run(host='0.0.0.0',port=PORT)