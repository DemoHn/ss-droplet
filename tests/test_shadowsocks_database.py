__author__ = 'Mingchuan'

import unittest
import sys

def get_file_directory():
    full_path = os.path.realpath(__file__)
    path,file = os.path.split(full_path)
    return path

sys.path.append(get_file_directory()+"/../")

from ss_server import ssServerDatabase,timeUtil


class testShadowsocksDatabase(unittest.TestCase):

    def __init__(self):
        # delete original database first to prevent data conflicts
        self.ss = ssServerDatabase("test")
        self.ss.deleteTestDatabase()

        # ssid,uid,avail_days,server_port,server_pid,password,method,s_type
        self.example_data = (1,3,1,9090,12345,"123456","rc4-md5","STABLE")
        pass
    # insertServerInstance
    # Last Edit: 2015-11-25
    def test_insert(self):
        example_data = self.example_data
        result = self.ss.insertServerInstance(
            example_data[0],
            example_data[1],
            example_data[2],
            example_data[3],
            example_data[4],
            example_data[5],
            example_data[6],
            example_data[7]
        )

        self.assertTrue(result)

    def test_updateMethod(self):
        # first update method
        self.ss.updateMethod(1,"aes-cfb-256")
        # then compare
        self.assertEqual(
            self.ss.getItem(1)["method"],
            "aes-cfb-256"
        )

    def test_updatePassword(self):
        # first update method
        # NOTICE : `password` is the password for a ss instance
        self.ss.updatePassword(1,"654321")
        # then compare
        self.assertEqual(
            self.ss.getItem(1)["password"],
            "654321"
        )

    def test_postpone(self):
        # get the original expire date
        item = self.ss.getItem(1)
        old_expire_stamp = timeUtil.getUTCtimestamp(item["expire_time"],0)

        # do postpone
        postpone_date = 3
        self.ss.postponeExpireDate(1,postpone_date)

        # get new expire date
        new_expire_stamp = timeUtil.getUTCtimestamp(self.ss.getItem(1)["expire_time"],0)
        self.assertEqual(int(new_expire_stamp) - int(old_expire_stamp) , postpone_date * 24 * 3600)

    def test_checkExpired(self):
        item = self.ss.checkExpiredInstance()
        self.assertFalse(len(item),0)
