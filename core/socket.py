__author__ = 'Mingchuan'

import socket, socketserver
from utils import returnModel
import threading
from config import config
from core.dispatch import new_service
from core.connect import connect
import json
# socket server
# using TCP protocol
# and it is asynchronous
# This server receives the request from client and HOST server
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class recvServer(socketserver.BaseRequestHandler):
    def sendSocket(self,status,info):
        rtn = returnModel("string")
        r_str = ""
        if status == "success":
            r_str = rtn.success(info)
        elif status == "error":
            r_str = rtn.error(info)

        rb = bytes(r_str,'utf-8')
        self.request.sendall(rb)

    # check if the socket IP is same from the HOST's IP registered in config.py
    # if "from" == "host"
    def checkHostIP(self):
        ip_addr = self.client_address[0]
        if ip_addr == config["CONTROL_SERVER_IP"]:
            return True
        else:
            return False
        pass
    # recv data format: (JSON)
    # e.g. :
    # {
    #   "from" : "host" | "client"
    #   "mac_addr" : {MAC Address} (only needed from "client")
    #   "command"  : "new" | "delete" | "connect" etc. (see the following description of commands)
    # }
    #
    # AND don't use try!
    # COMMAND LIST
    # 1) "ping" : just test if the server is OK. return "pong"
    # 2) "new" @params : "info":{ "max_traffic","max_devices","expire_timestamp","type"}
    # 3) "connect" @params: "mac_addr","service_idf"
    # 3) "revoke" @params : "service_idf"
    def handle(self):
        data = str(self.request.recv(1024).strip(), 'utf-8')
        try:
            json_data = json.loads(data)
        except ValueError:
            return self.sendSocket("error",400)
        finally:
            if json_data["from"] == "host":
                if self.checkHostIP() == False:
                    return self.sendSocket("error",403)
            # "ping"
            # just test if the server is OK. returns "pong"
            if json_data["command"] == "ping":
                return self.sendSocket("success","pong")
            # "new"
            # create new instance when
            elif json_data["command"] == "new":
                if json_data["from"] == "host":
                    max_traffic = json_data["info"]["max_traffic"]
                    max_devices = json_data["info"]["max_devices"]
                    expire_timestamp = json_data["info"]["expire_timestamp"]
                    type = json_data["info"]["type"]
                    dispatch_result = new_service(max_traffic,max_devices,type,expire_timestamp)

                    if dispatch_result == None:
                        return self.sendSocket("error",500)
                    elif dispatch_result["status"] == "error":
                        return self.sendSocket("error", dispatch_result["code"])
                    else:
                        # return service_idf!
                        return self.sendSocket("success",dispatch_result["info"])
                else:
                    return self.sendSocket("error",402)
            # connect to the remote server first.the server return the configuration.
            elif json_data["command"] == "connect":
                if json_data["from"] == "client":
                    mac_addr = json_data["mac_addr"]
                    service_idf = json_data["service_idf"]
                    result = connect(service_idf,mac_addr)

                    if result["status"] == "error":
                        return self.sendSocket("error",int(result["code"]))
                    else:
                        _data = json.dumps(result["info"])
                        return self.sendSocket("success",_data)
                    pass
                else:
                    return self.sendSocket("error",402)
            else:
                return self.sendSocket("error",405)
        pass

# start the server
def start_server():
    HOST, PORT = "0.0.0.0", config["SERVER_LISTEN_PORT"]
    server = ThreadedTCPServer((HOST,PORT),recvServer)
    ip, port = server.server_address
    # start a thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
#
# =================== CLIENT ===================
#