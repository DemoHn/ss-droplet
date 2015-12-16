__author__ = 'Nigshoxiz'

from model.model import RedisDatabase

class redisDevice(RedisDatabase):
    def __init__(self,service_idf):
        RedisDatabase.__init__(self)
        self.service_idf = service_idf
        pass

    def deviceInList(self,mac_addr):
        dev_key = "idf_"+self.service_idf
        if mac_addr != "" and mac_addr != None:
            return self.redis.sismember(dev_key,mac_addr)
        return False

    def newDevice(self,mac_addr):
        # using set
        dev_key = "idf_"+self.service_idf
        num = 0
        if mac_addr != "" and mac_addr != None:
            num = self.redis.sadd(dev_key,mac_addr)
        return num
        pass

    def countDevice(self):
        dev_key = "idf_"+self.service_idf
        return self.redis.scard(dev_key)

    def deleteDevice(self,mac_addr):
        dev_key = "idf_"+self.service_idf
        if mac_addr != "" and mac_addr != None:
            return self.redis.srem(dev_key,mac_addr)

    def deleteSet(self):
        dev_key = "idf_"+self.service_idf
        return self.redis.delete(dev_key)