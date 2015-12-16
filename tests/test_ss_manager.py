__author__ = 'Nigshoxiz'

import sys,os

def get_file_directory():
    full_path = os.path.realpath(__file__)
    path,file = os.path.split(full_path)
    return path

sys.path.append(get_file_directory()+"/../")

from proc.proc_ss import ssManagerProcess

ss = ssManagerProcess()

ss.createManagerProcess()

send = "ping"

ss.sendSocket(send)