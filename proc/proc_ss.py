__author__ = 'Mingchuan'
import os,subprocess,re
import signal
from string import Template
import socket
import json

class ssProcess:
    def __doc__(self):
        """
        control shadowsocks process
        """

    def __init__(self):
        self.local_port = 1080
        self.NAME = "ss-server"
        pass

    def get_file_directory(self):
        full_path = os.path.realpath(__file__)
        path,file = os.path.split(full_path)
        return path

    def execCommand(self,cmd,outdir):
        p = subprocess.Popen(cmd,shell=True,stdout = outdir,stderr = subprocess.STDOUT)
        return p.pid

    def execOut(self,cmd):
        p = subprocess.Popen(cmd,shell=True, stdout= subprocess.PIPE)
        (out,err) = p.communicate()
        out = out.decode("utf-8")
        return out

    def getIP(self):
        # "ifconfig" lists lots of information about IP address and other network configuration
        # we get domestic IP from here
        eth0_data = self.execOut("ifconfig eth0")

        re_ip = "inet addr:([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"
        # if can't read proper info
        if eth0_data.find("inet addr") > 0:
            m = re.search(re_ip,eth0_data)
            return m.group(1)
        else:
            return False
        pass

    def checkProcess(self,port=None):
        process = []
        if port == None:
            cmd = "netstat -putan | grep LISTEN | grep ss-server"
        else:
            cmd = "netstat -putan | grep LISTEN | grep ss-server | grep "+str(port)
        info = self.execOut(cmd)
        info_arr = info.split("\n")[:-1]

        for i in info_arr:
            process_model = {
                "pid":0,
                "port":0
            }
            i_arr = i.split()
            i_process = i_arr[6].split("/")

            ii_pid   = i_process[0]
            ii_pname = i_process[1]

            if ii_pname == self.NAME:
                process_model['pid'] = ii_pid
                process_model['port'] = i_arr[3].split(":")[1]
                process.append(process_model)

        return process

    def createProcess(self,port,password,timeout=100,method="rc4-md5"):
        if not self.getIP():
            return False
        else:
            HOST_IP = self.getIP()

        # kill the "ss" process if the port has been occupied (sometimes for restart the process)
        pid_array = self.checkProcess()
        for i in pid_array:
            if str(i['port']) == str(port):
                self.killProcess(int(i['pid']))

        cmd_content = Template("ss-server -s $HOST -p $PORT -l $LOCAL_PORT -k $PASSWORD -m $METHOD -t $TIMEOUT -u --fast-open &").substitute(
            HOST = HOST_IP,
            PORT = str(port),
            LOCAL_PORT = str(self.local_port),
            PASSWORD = password,
            METHOD = method,
            TIMEOUT = str(timeout)
        )

        def _exec(content,out_file):
            pid = self.execCommand(content,out_file)
            return pid

        # mkdir -p, ensure the directory exists
        self.execOut("mkdir -p "+self.get_file_directory()+"/log/")
        LOG_FILE = self.get_file_directory()+"/log/"+"port_"+str(port)+".log"
        file_log = open(LOG_FILE,'w',1)

        #f = Process(target=_exec,args=(cmd_content,file_log))
        #f.start()
        _exec(cmd_content,file_log)
        # get the exact pid
        pid_arr = self.checkProcess()
        for item in pid_arr:
            if str(item['port']) == str(port):
                return item['pid']
        return False

    def killProcess(self,pid):
        try:
            os.kill(int(pid),0)
        except OSError:
            print("[LOG] no such process!")
            return False
        else:
            #check again if the process name is called "ss-server"
            pname = self.execOut("ps -p "+str(pid)+" -o comm=")
            if pname.split("\n")[0] == self.NAME:
                os.kill(int(pid),signal.SIGTERM)
            else:
                print("[OUT] wrong PID")

# Update 2015-12-11
# shadowsocks-libev 大更新
# shadowsocks-libev 最近推出了一个ss-manager的功能，这个功能使得多用户管理和流量统计再也不是问题
# ssManagerProcess 自带UNIX socket通信方式来与ss-manager 进程通信
class ssManagerProcess(ssProcess):
    def __init__(self):
        ssProcess.__init__(self)
        self.NAME               = "ss-manager"
        self.SOCK_FILE          = "/var/run/ss_manager.sock"
        self.SS_SERVER_EXEC     = "/usr/bin/ss-server"

    def createManagerProcess(self):
        # check if ss-manager process already exists
        status = os.path.isfile(self.SOCK_FILE)
        if status == True:
            return None
        else:
            create_text = Template("$NAME --manager-address $UNIX_ADDR --executable $SS_SERVER_EXEC &").substitute(
                NAME = self.NAME,
                UNIX_ADDR = self.SOCK_FILE,
                SS_SERVER_EXEC = self.SS_SERVER_EXEC
            )
            self.execOut(create_text)

    def sendSocket(self,content):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        cnt = ""
        if content == "ping":
            cnt = content
        else:
            cnt = json.dumps(content)

        sock.connect(self.SOCK_FILE)
        sock.send(cnt)
        sock.close()
        recv = str(sock.recv(2048),"utf-8")
        print(recv)
        return recv






