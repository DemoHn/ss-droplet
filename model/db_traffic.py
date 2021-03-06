# Last Edit: 2015-12-12
from model.model import Database
from utils import returnModel, timeUtil
import traceback
from string import Template
import re

class serviceTraffic(Database):
    def __init__(self,env="normal"):
        self.env = env
        Database.__init__(self,env=self.env)
        self.createTable()
        self.rtn = returnModel()

    def createTable(self):
        # service_traffic
        #
        try:
            table_str = '''CREATE TABLE IF NOT EXISTS service_traffic(
            service_idf varchar(64) unique,
            upload_traffic FLOAT,
            download_traffic FLOAT,
            traffic_strategy text
            )'''
            cursor = self.cursor
            cursor.execute(table_str)
            self.connection.commit()
        except:
            traceback.print_exc()
        pass

    # create service_traffic
    # @params
    # service_idf : service identifier
    # upload_traffic : upload traffic of this identifier (unit:MB)
    # download_traffic: download traffic of this identifier (unit:MB)
    # traffic_strategy : strategy, determines the method
    # [strategy format]
    # e.g.:
    # traffic_strategy = AccountPerMonthStrategy,300
    # (reset the traffic to 300MB on the first day of every month)
    def createNewTraffic(self,service_idf,traffic_strategy):
        try:
            add_str = "INSERT INTO service_traffic (service_idf,upload_traffic,download_traffic,traffic_strategy) VALUES (%s,%s,%s,%s)"
            c = self.cursor

            INIT_UPLOAD_TRAFFIC   = 0.0
            INIT_DOWNLOAD_TRAFFIC = 0.0
            c.execute(add_str,[service_idf,INIT_UPLOAD_TRAFFIC,INIT_DOWNLOAD_TRAFFIC,traffic_strategy])

            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()

    def getTraffic(self,service_idf):
        try:
            get_str = "SELECT service_idf, upload_traffic, download_traffic,traffic_strategy FROM service_traffic WHERE service_idf = %s"
            c = self.cursor
            c.execute(get_str,[service_idf])
            data = c.fetchone()
            self.connection.commit()
            if data == None:
                return self.rtn.error(520)
            else:
                model = {
                    "service_idf" : data[0],
                    "upload_traffic" : data[1],
                    "download_traffic" : data[2],
                    "service_strategy": data[3]
                }
                return self.rtn.success(model)
        except Exception as e:
            traceback.print_exc()

    def deleteItem(self,service_idf):
        try:
            del_str = "DELETE FROM service_traffic WHERE service_idf = %s"
            c = self.cursor
            c.execute(del_str,[service_idf])
            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()

    # update traffic of this service_idf
    # NOTICE : unit is MB!!!!!!!!!!
    def updateTraffic(self,service_idf,new_upload_traffic,new_download_traffic):
        try:
            update_str = "UPDATE service_traffic SET upload_traffic = %s, download_traffic = %s WHERE service_idf = %s"
            c = self.cursor
            u_t = round(float(new_upload_traffic),3)
            d_t = round(float(new_download_traffic),3)
            c.execute(update_str,[u_t,d_t,service_idf])
            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()

    # if traffic exceeds, then pick the service_idf up and shutdown it
    def getExceedTrafficService(self):
        try:
            get_str = "SELECT service_traffic.service_idf FROM service_traffic INNER JOIN service_info \
                       ON service_info.service_idf = service_traffic.service_idf WHERE \
                       (service_traffic.upload_traffic + service_traffic.download_traffic) > service_info.max_traffic"

            c = self.cursor
            c.execute(get_str)
            data = c.fetchall()
            self.connection.commit()
            rtn_arr = []
            if data == None:
                return self.rtn.error(620)
            else:
                for rows in data:
                    rtn_arr.append(rows[0])

            return self.rtn.success(rtn_arr)
        except Exception as e:
            traceback.print_exc()

    def getTrafficInstancesByStrategy(self,strategy_name):
        try:
            # BE REALLY CAREFUL ABOUT SQL INJECTION!!!!
            # check if the strategy_name only contains characters and end with "Strategy"
            re_str = "^[a-zA-Z]+Strategy$"
            re_exp = re.compile(re_str)
            res = re_exp.match(strategy_name)

            if res == None:
                return self.rtn.error(500)
            else:
                sel_str = Template("SELECT service_idf, traffic_strategy FROM service_traffic WHERE `traffic_strategy` LIKE '%$strategy_name%'").substitute(
                    strategy_name = strategy_name
                )

                c = self.cursor
                c.execute(sel_str)
                data = c.fetchall()
                self.connection.commit()
                data_model = []
                if data == None:
                    return self.rtn.success([])
                else:
                    for rows in data:
                        info = {
                            "service_idf" : rows[0],
                            "service_strategy": rows[1]
                        }
                        data_model.append(info)
                    return self.rtn.success(data_model)
        except Exception as e:
            traceback.print_exc()

    def resetZero(self,service_idf):
        try:
            c = self.cursor
            reset_str = "UPDATE service_traffic SET upload_traffic = %s, download_traffic = %s WHERE service_idf = %s"
            c.execute(reset_str,[0.0,0.0,service_idf])
            self.connection.commit()
            return self.rtn.success(200)
        except Exception as e:
            traceback.print_exc()
