__author__ = 'Mingchuan'

import unittest
import sys,os

def get_file_directory():
    full_path = os.path.realpath(__file__)
    path,file = os.path.split(full_path)
    return path

sys.path.append(get_file_directory()+"/../")

class testShadowsocksDatabase(unittest.TestCase):
    def setUp(self):
        pass
