__author__ = 'Nigshoxiz'
# last edit: 2016-1-7
from model.model import RedisDatabase
from random import randint
"""
redisHeartBeatPacket:
A redis-based hash table that stores heart beat packet ready to send to host server.
1)
key name: hb_packet
fields  :

-- packet_tag  : <stores current packet tag, if the host server responses with it, the value is cleared to 0.>
-- expire_idfs : <a serialized set that contains expired IDFs.>
-- traffic_exceed_idfs : <a serialized set that contains exceed-traffic IDFs.>

-- XXXXX_upload   : <upload traffic of a service>
-- XXXXX_download : <download traffic of a service>
   (More...)
   (XXXX is service_idf)

-- XXXXX_du      : <upload delta traffic>
-- XXXXX_dd      : <download delta traffic>
NOTE: for these XXXX_upload field, if the packet send successfully, the value will be subtracted and updated to represent a "delta" traffic;
If not, the value will just be updated

2) set name:curr_idfs

"""
class redisHeartBeatPacket(RedisDatabase):
    def __init__(self):
        RedisDatabase.__init__(self)
        self.key_name = "hb_packet"
        self.set_name = "curr_idfs"
        # reset packet_tag
        self.redis.hset(self.key_name,"packet_tag",0)
        self.redis.hset(self.key_name,"expire_idfs","")
        self.redis.hset(self.key_name,"traffic_exceed_idfs","")
        pass

    def setPacketTag(self,tag):
        return self.redis.hset(self.key_name,"packet_tag",tag)

    def getPacketTag(self):
        return self.__hget(self.key_name,"packet_tag")

    def clearPacketTag(self,tag):
        curr_tag = self.__hget(self.key_name,"packet_tag")
        if curr_tag == str(tag):
            return self.redis.hset(self.key_name,"packet_tag",0)
        else:
            return None

    def __hget(self,key,field):
        b = self.redis.hget(key,field)
        return b.decode("utf-8")

    def updateExpireIdfs(self,idfs_arr):
        # get str and convert to array
        curr_idfs_str = self.__hget(self.key_name,"expire_idfs")

        print(curr_idfs_str)
        if curr_idfs_str == "":
            curr_idfs_arr = []
        else:
            curr_idfs_arr = curr_idfs_str.split(",")

        # if previous packet succeed to send, then tag should be zero and clear old info.
        if int(self.getPacketTag()) == 0:
            self.deleteObsoleteIdfs(idfs_arr)
            __str = ",".join(idfs_arr)
            return self.redis.hset(self.key_name,"expire_idfs",__str)
        else:
            # merge two arrays
            for item in idfs_arr:
                if (item in curr_idfs_arr) == False:
                    curr_idfs_arr.append(item)
            #serialization
            _str = ",".join(curr_idfs_arr)
            return self.redis.hset(self.key_name,"expire_idfs",_str)

    def updateTrafficExceedIdfs(self,idfs_arr):
        # get str and convert to array
        curr_idfs_str = self.__hget(self.key_name,"traffic_exceed_idfs")

        if curr_idfs_str == "":
            curr_idfs_arr = []
        else:
            curr_idfs_arr = curr_idfs_str.split(",")

        # if previous packet succeed to send, then tag should be zero and clear old info.
        if int(self.getPacketTag()) == 0:
            self.deleteObsoleteIdfs(idfs_arr)
            __str = ",".join(idfs_arr)
            return self.redis.hset(self.key_name,"traffic_exceed_idfs",__str)
        else:
            # merge two arrays
            for item in idfs_arr:
                if (item in curr_idfs_arr) == False:
                    curr_idfs_arr.append(item)
            #serialization
            _str = ",".join(curr_idfs_arr)
            return self.redis.hset(self.key_name,"traffic_exceed_idfs",_str)

    # unit: MB
    def updateTraffic(self,service_idf,u_t,d_t):
        field_u = service_idf + "_upload"
        field_d = service_idf + "_download"
        field_du = service_idf + "_du"
        field_dd = service_idf + "_dd"

        # add idf into curr_idfs (set)
        self.redis.sadd(self.set_name,service_idf)

        # if no values in, then set it
        if self.__hget(self.key_name,field_u) == None or \
            self.__hget(self.key_name,field_d) == None or \
            self.__hget(self.key_name,field_du) == None or \
            self.__hget(self.key_name,field_dd) == None:

            self.redis.hset(self.key_name,field_u,0)
            self.redis.hset(self.key_name,field_d,0)
            self.redis.hset(self.key_name,field_du,0)
            self.redis.hset(self.key_name,field_dd,0)

        # if succeed, both upload and delta_uplaod filed should update to the newest
        if int(self.getPacketTag()) == 0:
            # upload
            old_u_t = float(self.__hget(self.key_name,field_u))
            delta   = float(u_t) - old_u_t
            # if old_u_t is larger than new_u_t, that means the droplet must have been restarted and traffic has calculated again
            if float(u_t) < old_u_t:
                delta = 0.0
            self.redis.hset(self.key_name,field_du,delta)
            self.redis.hset(self.key_name,field_u,float(u_t))
            # download
            old_d_t = float(self.__hget(self.key_name,field_d))
            delta   = float(d_t) - old_d_t
            # if old_d_t is larger than new_d_t, that means the droplet must have been restarted and traffic has calculated again
            if float(d_t) < old_d_t:
                delta = 0.0
            self.redis.hset(self.key_name,field_dd,delta)
            self.redis.hset(self.key_name,field_d,float(d_t))
        else:
            du_t = float(self.__hget(self.key_name,field_du))
            old_u_t = float(self.__hget(self.key_name,field_u))

            new_du = du_t + float(u_t) - old_u_t
            if float(u_t) < old_u_t:
                new_du = du_t

            self.redis.hset(self.key_name,field_du,new_du)
            #download
            dd_t = float(self.__hget(self.key_name,field_dd))
            old_d_t = float(self.__hget(self.key_name,field_d))

            new_dd = dd_t + float(d_t) - old_d_t
            if float(d_t) < old_d_t:
                new_dd = dd_t

            self.redis.hset(self.key_name,field_dd,new_dd)

    def deleteObsoleteIdfs(self,obsolete_idfs_arr):
        for item in obsolete_idfs_arr:
            self.redis.srem(self.key_name,item)
            self.redis.hdel(self.key_name,[item+"_upload",item+"_download"])
        return None

    def generatePakcetContent(self):
        pack_json = {
            "command":"heart_beat",
            "expire_idfs":[],
            "traffic_exceed_idfs":[],
            "delta_traffic":[], # format: [<idf,du,dd,...>] e.g:["24def",3.0,4.0,"123fw",5.0,2.0]
            "package_tag":""
        }

        # generate a tag randomly or maintain the original one
        if int(self.getPacketTag()) == 0:
            tag =  randint(1000000,9999999)
            pack_json["package_tag"] = tag
            self.setPacketTag(tag)
        else:
            pack_json["package_tag"] = self.getPacketTag()

        expire_idfs_str = self.__hget(self.key_name,"expire_idfs")
        traffic_exceed_str = self.__hget(self.key_name,"traffic_exceed_idfs")

        if expire_idfs_str != "":
            pack_json["expire_idfs"] = expire_idfs_str.split(",")

        if traffic_exceed_str != "":
            pack_json["traffic_exceed_idfs"] = expire_idfs_str.split(",")

        # get all idfs in current_idf
        _idfs = self.redis.smembers(self.set_name)

        for item in _idfs:
            item = item.decode("utf-8")
            idf_du_t = float(self.__hget(self.key_name,item+"_du"))
            idf_dd_t = float(self.__hget(self.key_name,item+"_dd"))
            
            info_arr = [item,idf_du_t,idf_dd_t]
            pack_json["delta_traffic"].extend(info_arr)

        return pack_json
