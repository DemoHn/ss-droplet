# ss-droplet

## 简介  
`ss-droplet` 是一个shadowsocks多用户管理程序。  
一般部署于墙外的代理服务器（下称droplet服务器）上,让一个droplet服务器能够同时给多个用户提供shadowsocks网络加速服务。故而本管理程序面向的主要是各大“上网加速”类网站的站长们。
  
它具有以下功能：  

- `shadowsocks`流量统计

- 分配及管理多个`shadowsocks`账号

- 与“主机” _(Control Server)_ 进行通信
  
本程序完全使用python语言编写，目前仅在linux环境下经过测试。

`ss-droplet`的名字来源于`digitalOcean`：这家来自美国的VPS服务商把他们的每一个实例都叫作 `droplet`。能使用这个程序的人应该手里会有不只一台服务器。  

> 每一台服务器都是一个小水滴，汇聚起来就成为了大海。
> 

## 安装与配置
---------------------

本程序的运行环境是python3, 涉及到的后台数据库有`redis`和`mariaDB`(mysql)

在Ubuntu操作系统下：

`apt-get install python3-pip mariadb-server mariadb-client redis-server`

在随后的安装界面中设置mariadb的密码;

再然后安装python3模块：  
`pip3 install redis apscheduler cymysql`

复制源代码到服务器中:  
`git clone https://github.com/DemoHn/ss-droplet`

依据`config.py.example`修改配置：  
```
cd ss-droplet  
cp config.py.example config.py  
vi config.py  
```
在`config["MYSQL_PASSWORD"]`这一项中填上自己的mariadb密码。    
__注：__ 下一节会介绍`config["CONTROL_SERVER_IP"]` 的含义，如果您已经知道了它的作用，那么就直接填上"主机"的IP地址吧。(目前只试过ipv4)

## 两种工作模式
--------------------------------

本程序支持两种工作模式:  
1. 主机模式 (control mode)
2. 独立模式 (independent mode)

### 主机模式 (推荐)
所谓“主机”，就是“网络加速”站的站长同时运行一个主站用于管理所有的用户和账号。主机在负责管理用户所购买的所有账号的同时负责与所有droplet服务器进行交互。  
大部分情况下，droplet服务器只接受来自"主机"的`socket`请求。  
所以...若是要启用主机模式的话，在`config["CONTROL_SERVER_IP"]`处就要写上主机的IP地址。

在主机模式下，用户的基本交互流程如下：  
1. 用户向主机发送申请shadowsocks账号请求。  
2. 主机向droplet服务器发送申请请求:`new`。  
3. droplet服务器返回shadowsocks账号的具体信息。  
4. 主机向用户返回此账号的`service_idf` (service identifier)和目标droplet服务器的地址。  
5. 用户根据`service_idf`和droplet服务器的地址直接向droplet服务器发送`connect`请求，得到shadowsocks配置参数。  
6. 连接成功。  

### 独立模式
“独立模式”就是指只有droplet服务器和用户，没有“主机”。  
在`config["CONTROL_SERVER_IP"]`下留空即可。

细节与“主机模式”类似，此处不再详述。

## Socket API
----------------------------------

与droplet服务器的所有通信采用`socket`通信方式。TCP和UDP监听端口见`config.py`中`config["SERVER_LISTEN_PORT"]`。  
__注意：__ 无论是在主机模式还是在独立模式下，发送中的"from"参数都是一样的，并不因为在“独立模式”下没有`host`的存在就不写`host`了。  

发送和返回都是JSON格式。_当然把JSON转成字符串再发送这个应该不用提醒了吧~~_  
发送全部采用 __TCP socket__ 请求。  

返回值无非两种情况：  
1. success  (code=200)  
`{"status": "success", "code": 200, "info":****}`

2. error (code=XXX)  
`{"status": "error", "code": XXX, "info":<error info>}`  

__发送API：__  

### 1. Ping 
_发送:_   
```
{  
    "command":"ping"  
}  
```  
_返回:_  
```
{"status": "success", "code": 200, "info":"ping"}
```
  
### 2. Create A brand-new shadowsocks service
_发送:_  
```
{  
    "from":"host",  
    "command":"new",  
    "info":{  
        "max_traffic": 100*1000, # 当前最多可用的流量 (单位：MB)   
        "max_devices": 5, # 限制最多连接设备数  
        "expire_timestamp"：234567812, # 服务到期时间的UNIX timesatmp (in UTC)  
        "traffic_strategy":"AccountPerDayStrategy,10", # 流量管理策略.[1]  
        "type": "shadowsocks-obfs" # 服务类型[2]  
    }  
}  
```

注[1]: 流量管理策略写法格式如下：  
`<service_strategy>,<max_traffic>`  
前者是策略名称,目前支持`AccountPerDayStrategy`和`AccountPerMonthStrategy`两种：前者是每天重置一次流量，后者是每月重置的流量。
`<max_traffic>`是重置的流量大小。单位是MB。  

注[2]: 服务类型支持两种：
`shadowsocks-obfs`和`shadowsocks`
  
前者的源代码见[shadowsocks-obfs](https://github.com/breakwa11/shadowsocks-rss)  
推荐使用前者。`ss-droplet`内置了对`shadowsocks-obfs`的支持。

对于后者，请自行安装[shadowsocks-libev](https://github.com/clowwindy/shadowsocks-libev/tree/fastopen)    
`shadowsocks`模式暂不支持流量统计功能。  

_返回:_  
```
{"status": "success", "code": 200, "info":{  
    "expire_timestamp": 234567812,  
    "service_idf": "faoee23f", #服务标识符,作为标记这个shadowsocks账户的唯一标记  
    "config": { <service_configuration> }
}}  
```

### 3. Connect To the Server to get the service
_发送:_  
```
{  
    "from":"client",  
    "command":"connect",  
    "mac_addr":"12:34:56:78:90:AB",  #设备的MAC地址    
    "service_idf":"ajofjwve2"  #服务标识符  
}  
```
_返回:_  
```
{"status": "success", "code": 200, "info":{ <service_configuration> }}
```

### 4. Revoke the service even if it is still valid
(BE REALLY CAREFUL)  

_发送:_  
```
{  
    "from":"host",  
    "command":"revoke",  
    "service_idf":"ajofjwve2"  
}  
```
_返回:_  
```
{"status": "success", "code": 200, "info":200}
```

### 5. Postpone the expire time of a service
(BE REALLY CAREFUL)  

_发送:_  
```
{  
    "from":"host",  
    "command":"postpone",  
    "service_idf":"ajofjwve2",  
    "postpone_timestamp":12345678 #(UTC timestamp!!!)
}  
```
_返回:_  
```
{"status": "success", "code": 200, "info":200}
```

### 6. Increase the available traffic for a service 
(BE REALLY CAREFUL)  

_发送:_  
```
{  
    "from":"host",  
    "command":"increase_traffic",  
    "service_idf":"ajofjwve3",  
    "traffic": *** (unit:MB)
}  
```
_返回:_  
```
{"status": "success", "code": 200, "info":200}
```

### 7. Decrease the available traffic for a service 
(BE REALLY CAREFUL)  

_发送:_  
```
{  
    "from":"host",  
    "command":"decrease_traffic",  
    "service_idf":"ajofjwve3",  
    "traffic": *** (unit:MB)
}  
```
_返回:_  
```
{"status": "success", "code": 200, "info":200}
```

## 与shadowsocks-obfs的关系
-------------------------------------
`ss-droplet`自带对[shadowsocks-obfs](https://github.com/breakwa11/shadowsocks/tree/manyuser)的支持。
这里只是把config.json在运行时给覆盖了一下，并没有修改里面的源代码。    


## 开源协议
------------------------------------
GPL ,就这样吧。