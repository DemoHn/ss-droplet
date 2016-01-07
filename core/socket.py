__author__ = 'Nigshoxiz'

import socket, socketserver
from utils import returnModel
import threading
from config import config
from core.dispatch import new_service
from core.connect import connect
from core.revoke import revoke
from core.postpone import postpone, increase_traffic,decrease_traffic
import json

from model.db_traffic import serviceTraffic
# socket server
# using TCP protocol
# and it is asynchronous
# This server receives the request from client and HOST server

class ThreadedUDPServer(socketserver.ThreadingMixIn,socketserver.UDPServer):
    pass
class recvServer_UDP(socketserver.BaseRequestHandler):
    def sendSocket(self,status,info):
        rtn = returnModel("string")
        r_str = ""
        if status == "success":
            r_str = rtn.success(info)
        elif status == "error":
            r_str = rtn.error(info)

        rb = bytes(r_str,'utf-8')
        # dest
        socket = self.request[1]
        socket.sendto(rb, self.client_address)

    def handle(self):
        data = str(self.request[0].strip(),"utf-8")
        handle_UDP(self,data)

def handle_UDP(serv,data):
    try:
        jdata = json.loads(data)
        if jdata["command"] == "ping":
            serv.sendSocket("success","pong")
        elif jdata["command"] == "heart_beat":
            # TODO
            pass
        else:
            serv.sendSocket("error",405)
    except TypeError:
        serv.sendSocket("error",400)
    pass

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
        if ip_addr == config["CONTROL_SERVER_IP"]\
                or config["CONTROL_SERVER_IP"] == "":
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
    # COMMAND LIST
    # 1) "ping" : just test if the server is OK. return "pong"
    # 2) "new" @params : "from","info":{ "max_traffic","max_devices","expire_timestamp","type","traffic_strategy"}
    # 3) "connect" @params: "from","mac_addr","service_idf"
    # 4) "revoke" @params : "from","service_idf"
    # 5) "postpone" @params: "from","service_idf","postpone_timestamp"
    def handle(self):
        data = str(self.request.recv(1024).strip(), 'utf-8')
        try:
            json_data = json.loads(data)
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
                    traffic_strategy = json_data["info"]["traffic_strategy"]
                    service_type = json_data["info"]["type"]
                    dispatch_result = new_service(max_traffic,max_devices,service_type,expire_timestamp,strategy=traffic_strategy)

                    if dispatch_result == None:
                        return self.sendSocket("error",500)
                    elif dispatch_result["status"] == "error":
                        return self.sendSocket("error", dispatch_result["code"])
                    else:
                        # return service_idf and expire_date
                        rtn_model = {
                            "expire_timestamp": int(expire_timestamp),
                            "service_idf"     : dispatch_result["info"]["service_idf"],
                            "config"          : dispatch_result["info"]["config"]
                        }
                        return self.sendSocket("success",rtn_model)
                else:
                    return self.sendSocket("error",402)
            # connect to the remote server first.the server return the configuration.
            elif json_data["command"] == "connect":
                if json_data["from"] == "client":
                    mac_addr = json_data["mac_addr"]
                    service_idf = json_data["service_idf"]

                    #OP
                    result = connect(service_idf,mac_addr)

                    if result["status"] == "error":
                        return self.sendSocket("error",int(result["code"]))
                    else:
                        _data = json.dumps(result["info"])
                        return self.sendSocket("success",_data)
                    pass
                else:
                    return self.sendSocket("error",402)
            # if the instance expired , just kill it
            # if not necessary, plz don't call IT
            elif json_data["command"] == "revoke":
                if json_data["from"] == "host":
                    service_idf = json_data["service_idf"]

                    #OP
                    res         = revoke(service_idf)

                    if res["status"] == "error":
                        return self.sendSocket("error",res["code"])
                    else:
                        return self.sendSocket("success",200)
                else:
                    return self.sendSocket("error",402)

            # postpone
            elif json_data["command"] == "postpone":
                if json_data["from"] == "host":
                    service_idf      = json_data["service_idf"]
                    expire_timestamp = int(json_data["postpone_timestamp"])
                    res              = postpone(service_idf,expire_timestamp)

                    if res["status"] == "error":
                        return self.sendSocket("error",res["code"])
                    else:
                        return self.sendSocket("success",200)
                else:
                    return self.sendSocket("error",402)

            elif json_data["command"] == "increase_traffic":
                if json_data["from"] == "host":
                    service_idf      = json_data["service_idf"]
                    traffic          = json_data["traffic"]

                    res              = increase_traffic(service_idf,traffic)
                    if res["status"] == "error":
                        return self.sendSocket("error",res["code"])
                    else:
                        return self.sendSocket("success",200)
                else:
                    return self.sendSocket("error",402)

            elif json_data["command"] == "decrease_traffic":
                if json_data["from"] == "host":
                    service_idf      = json_data["service_idf"]
                    traffic          = json_data["traffic"]

                    res              = decrease_traffic(service_idf,traffic)
                    if res["status"] == "error":
                        return self.sendSocket("error",res["code"])
                    else:
                        return self.sendSocket("success",200)
                else:
                    return self.sendSocket("error",402)

            elif json_data["command"] == "adjust_quota":
                if json_data["from"] == "host":
                    new_quota        = json_data["new_quota"]

                    #注意：这个调整只是临时的，服务只要一重启就会恢复原状
                    config["SERVICE_QUOTA"] = int(new_quota)
                    return self.sendSocket("success",200)
                else:
                    return self.sendSocket("error",402)
            # get real time traffic (debug)
            elif json_data["command"] == "__get_traffic":
                if json_data["from"] == "host":
                    service_idf     = json_data["service_idf"]
                    trafficDB       = serviceTraffic()
                    traffic         = trafficDB.getTraffic(service_idf)
                    return self.sendSocket("success",traffic["info"])
                else:
                    return self.sendSocket("error",402)
            else:
                return self.sendSocket("error",405)
        except ValueError:
            return self.sendSocket("error",400)
        pass

# start the server
def start_socket_server():
    HOST, PORT = "0.0.0.0", config["SERVER_LISTEN_PORT"]
    server = ThreadedTCPServer((HOST,PORT),recvServer)
    ip, port = server.server_address
    # start a thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # start a thread (UDP Server)
    PORT_UDP = config["SERVER_LISTEN_PORT_UDP"]
    server_udp = ThreadedUDPServer((HOST,PORT_UDP),recvServer_UDP)
    server_thread_udp = threading.Thread(target=server_udp.serve_forever)
    server_thread_udp.daemon = True
    server_thread_udp.start()

    return (server,server_udp)

def stop_socket_server(server):
    server.shutdown()

#
# =================== CLIENT ===================
#

def send_socket_request(dest_ip,dest_port,data,type="TCP"):
    rtn = returnModel()
    dest_port = int(dest_port)
    if type == "TCP":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(5)
            sock.connect((dest_ip,dest_port))
            sock.settimeout(None)
            sock.sendall(bytes(data + "\n","utf-8"))

            # recv data
            recv = str(sock.recv(2048),"utf-8")
            sock.close()

            return json.loads(recv)
        except socket.timeout:
            return rtn.error(801)

    elif type == "UDP":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(bytes(data + "\n","utf-8"),(dest_ip,dest_port))
            return rtn.success(200)
        except Exception as e:
            return rtn.error(800)
