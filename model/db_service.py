# Last Edit: 2015-12-4
from model.model import Database
from utils import returnModel, timeUtil
import traceback

class serviceInfo(Database):
    def __init__(self,env="normal"):
        self.env = env
        Database.__init__(self,env = self.env)
        self.createTable()
        self.rtn = returnModel()

    def createTable(self):
        # ss database table
        # NOTICE: start_time & expire_time are ALL UTC TIME !!!!!!!!!!!!!!
        try:
            table_str = '''CREATE TABLE IF NOT EXISTS service_info(
            service_idf varchar(64) unique,
            max_devices integer,
            max_traffic float,
            expire_time datetime,
            service_type text
            )'''
            cursor = self.cursor
            cursor.execute(table_str)
            self.connection.commit()
        except:
            traceback.print_exc()
        pass

    # create service
    # @params
    # service_idf : service identifier
    # max_devices : for this service ,the max number of allowed devices. (each device is marked by its MAC address)
    # max_traffic : max traffic allowed in some time.(maybe a month?) and it should be reset when a new period comes
    # expire_time : it is available until this time.
    def createNewService(self,service_idf,max_devices,max_traffic,expire_timestamp,service_type):
        try:
            add_str = "INSERT INTO service_info (service_idf,max_devices,max_traffic,expire_time,service_type) VALUES (%s,%s,%s,%s,%s)"
            c = self.cursor
            expire_str = timeUtil.getReadableTime(int(expire_timestamp),0)
            print(service_idf)
            print(expire_str)
            c.execute(add_str,[service_idf,int(max_devices),float(max_traffic),expire_str,service_type])

            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()

    def getItem(self,service_idf):
        try:
            get_str = "SELECT service_idf, max_devices, max_traffic, expire_time,service_type FROM service_info WHERE service_idf = %s"
            c = self.cursor
            c.execute(get_str,[service_idf])
            data = c.fetchone()

            if data == None:
                return self.rtn.error(520)
            else:
                model = {
                    "service_idf" : data[0],
                    "max_devices" : data[1],
                    "max_traffic" : data[2],
                    "expire_time" : data[3],
                    "service_type": data[4]
                }
                return self.rtn.success(model)
        except Exception as e:
            traceback.print_exc()

    def getItems(self):
        try:
            get_str = "SELECT service_idf, max_devices, max_traffic, expire_time,service_type FROM service_info"
            c = self.cursor
            c.execute(get_str)
            data = c.fetchone()
            model_arr = []
            if data == None:
                return self.rtn.error(520)
            else:
                for rows in data:
                    model = {
                        "service_idf" : rows[0],
                        "max_devices" : rows[1],
                        "max_traffic" : rows[2],
                        "expire_time" : rows[3],
                        "service_type": rows[4]
                    }

                    model_arr.append(model)
                return self.rtn.success(model_arr)
        except Exception as e:
            traceback.print_exc()

    def deleteItem(self,service_idf):
        try:
            del_str = "DELETE FROM service_info WHERE service_idf = %s"
            c = self.cursor
            c.execute(del_str,[service_idf])
            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()

    # and next... check Expired Item
    # the term "expired" means current time if later than the expired time
    def checkExpiredService(self):
        try:
            expire_str = "SELECT service_idf FROM service_info WHERE NOW() > expire_time"
            c = self.cursor
            data = c.execute(expire_str)

            model = []
            if data == None:
                return self.rtn.error(620)
            for rows in data:
                model.append(rows[0])
            return self.rtn.success(model)
        except Exception as e:
            traceback.print_exc()
        pass

    def checkDeviceLimit(self,service_idf):
        try:
            check_str = "SELECT max_devices FROM service_info WHERE service_idf = %s"
            c = self.cursor
            c.execute(check_str,[service_idf])

            data = c.fetchone()
            if data == None:
                return self.rtn.error(520)
            else:
                return self.rtn.success(data[0])
        except Exception as e:
            traceback.print_exc()

    def checkMaxTraffic(self,service_idf):
        try:
            check_str = "SELECT max_traffic FROM service_info WHERE service_idf = %s"
            c = self.cursor
            c.execute(check_str,[service_idf])

            data = c.fetchone()
            if data == None:
                return self.rtn.error(520)
            else:
                return self.rtn.success(data[0])
        except Exception as e:
            traceback.print_exc()

    def countActiveService(self):
        try:
            count_str = "SELECT count(*) FROM service_info"
            c = self.cursor
            c.execute(count_str)

            data = c.fetchone()
            if data == None:
                return self.rtn.error(520)
            else:
                return self.rtn.success(int(data[0]))
        except Exception as e:
            traceback.print_exc()

    # update sth
    def updateExpireTimestamp(self,service_idf,expire_timestamp):
        try:
            c = self.cursor
            expire_time = timeUtil.getReadableTime(expire_timestamp,0)
            update_str = "UPDATE service_info SET expire_time = %s WHERE service_idf = %s"
            c.execute(update_str,[expire_time,service_idf])
            self.connection.commit()

            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()

    def resetTraffic(self,service_idf,traffic):
        try:
            traffic = float(traffic)
            c = self.cursor
            update_str = "UPDATE service_info SET max_traffic = %s WHERE service_idf = %s"
            c.execute(update_str,[traffic,service_idf])

            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()
