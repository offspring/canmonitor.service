#!/usr/bin/python3
"""Can NMEA 2000 monitor service"""

import datetime
import os
import sys
from pathlib import Path

import can


class RotatingFile(object):
    def __init__(self, directory="", filename="foo", max_file_size=10 * 1024 * 102):
        self.ii = 1
        self.directory, self.filename = directory, filename
        self.max_file_size = max_file_size
        self.finished, self.fh = False, None
        self.open()

    def rotate(self):
        """Rotate the file, if necessary"""
        if os.stat(self.filename_template).st_size > self.max_file_size:
            self.close()
            self.open()

    def open(self):
        self.ts = self.timestamp_template
        self.fh = open(self.filename_template, "w")

    def write(self, text=""):
        self.fh.write(text)
        self.fh.flush()
        self.rotate()

    def close(self):
        self.fh.close()

    @property
    def timestamp_template(self):
        # return datetime.datetime.now().replace(microsecond=0).isoformat().replace("-")
        return datetime.datetime.now().replace(microsecond=0).strftime("%Y%m%dT%H%M%S")

    @property
    def filename_template(self):
        return str(Path(self.directory, f"{self.filename}.{self.ts}"))


def parse_can_id(canid: int):
    PF = (canid >> 16) & 0xFF
    PS = (canid >> 8) & 0xFF
    RDP = (canid >> 24) & 3  # Use R + DP bits

    src = (canid >> 0) & 0xFF
    pri = (canid >> 26) & 0x7
    if PF < 240:
        # PDU1 format, the PS contains the destination address
        dst = PS
        pgn = (RDP << 16) + (PF << 8)
    else:
        # PDU2 format, the destination is implied global and the PGN is extended
        dst = 0xFF
        pgn = (RDP << 16) + (PF << 8) + PS
    return f"{pri},{pgn},{src},{dst}"


def dump_in_canboat(canid: int, data: bytearray):
    """dump in canboat candump2analyzer"""
    # candump2analyzer format
    # "2024-07-29-12:55:17.133,7,126993,141,255,8,30,75,7c,cf,ff,ff,ff,ff"
    # "2024-07-29-12:48:36.815,4,129038,0,255,2,e4,ff"
    # "2024-07-29-12:48:36.815,3,129029,1,255,8,00,2b,c1,dc,4d,8e,3d,29"
    dtutc = datetime.datetime.now(datetime.timezone.utc)
    ts = f"{dtutc.strftime('%Y-%m-%d-%H:%M:%S')}.{int(dtutc.microsecond/1000):03d}"
    return f"{ts},{parse_can_id(canid)},{len(data)},{','.join('{:02x}'.format(x) for x in data)}"


def dump_in_candmp(canid: int, data: bytearray):
    """dump in candmp"""
    # candump format
    # "  can0  1DF0118D   [8]  30 75 7C CF FF FF FF FF"
    # "  can0  09F80101   [8]  4F 0E 76 18 A6 F7 2B D4"
    return f"  can0  {canid:08X}   [{len(data)}]  {' '.join('{:02X}'.format(x) for x in data)}"


def main():
    """main"""

    output_file = RotatingFile(
        directory="/home/pi/canmonitor.service/logs",
        filename="tempest.log",
        max_file_size=100 * 1024 * 1024,
    )

    with can.Bus(interface="socketcan", channel="can0", bitrate=250000) as bus:
        for msg in bus:
            # output = dump_in_candmp(msg.arbitration_id, msg.data)
            output = dump_in_canboat(msg.arbitration_id, msg.data)
            output_file.write(text=f"{output}\n")
            #print(output)


if __name__ == "__main__":
    main()
