#!/usr/bin/python3
"""Can NMEA 2000 monitor service"""

import datetime
import os
import sys
from pathlib import Path

import can

class RotatingFile(object):
    def __init__(self, directory='', filename='foo', max_file_size=5*1024*102):
        self.ii = 1
        self.directory, self.filename      = directory, filename
        self.max_file_size                 = max_file_size
        self.finished, self.fh             = False, None
        self.ts = datetime.datetime.now().replace(microsecond=0).isoformat()
        self.open()

    def rotate(self):
        """Rotate the file, if necessary"""
        if (os.stat(self.filename_template).st_size>self.max_file_size):
            self.close()
            self.open()

    def open(self):
        self.ts = datetime.datetime.now().replace(microsecond=0).isoformat()        
        self.fh = open(self.filename_template, 'w')

    def write(self, text=""):
        self.fh.write(text)
        self.fh.flush()
        self.rotate()

    def close(self):
        self.fh.close()

    @property
    def filename_template(self):
        return str(Path(self.directory, f"{self.filename}.{self.ts}"))

def dump_array(byte_array):
    """dump_aray"""
    return ' '.join('{:02X}'.format(x) for x in byte_array).upper()

def main():
    """main"""

    output_file = RotatingFile(directory="/home/pi/canmonitor.service/logs", filename="tempest.log", max_file_size=100*1024*1024)

    with can.Bus(interface='socketcan', channel='can0', bitrate=250000) as bus:
        for msg in bus:
            # "  can0  09F80101   [8]  4F 0E 76 18 A6 F7 2B D4"
            output = f"  can0  {msg.arbitration_id:08X}   [{len(msg.data)}]  {dump_array(msg.data)}"
            output_file.write(text=f"{output}\n")
            print(output)

if __name__ == '__main__':
    main()
