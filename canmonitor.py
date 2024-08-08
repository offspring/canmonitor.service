#!/usr/bin/python3
"""Can NMEA 2000 monitor service"""

import argparse
import datetime
import os
import sys
from pathlib import Path

import can


class RotatingFile(object):
    """RotatingFile"""

    def __init__(self, directory="", filename="foo", max_file_size=10 * 1024 * 102):
        """"""
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
        """open file"""
        self.ts = self.timestamp_template
        self.fh = open(self.filename_template, "w", encoding="utf-8")

    def write(self, text=""):
        """write to a file"""
        self.fh.write(text)
        self.fh.flush()
        self.rotate()

    def close(self):
        """close file"""
        self.fh.close()

    @property
    def timestamp_template(self):
        """timestamp template"""
        return datetime.datetime.now().replace(microsecond=0).strftime("%Y%m%dT%H%M%S")

    @property
    def filename_template(self):
        """filename template"""
        return str(Path(self.directory, f"{self.filename}.{self.ts}"))


def parse_can_id(canid: int):
    """parse can id"""
    pf = (canid >> 16) & 0xFF
    ps = (canid >> 8) & 0xFF
    rdp = (canid >> 24) & 3  # Use R + DP bits

    src = (canid >> 0) & 0xFF
    pri = (canid >> 26) & 0x7
    if pf < 240:
        # PDU1 format, the ps contains the destination address
        dst = ps
        pgn = (rdp << 16) + (pf << 8)
    else:
        # PDU2 format, the destination is implied global and the PGN is extended
        dst = 0xFF
        pgn = (rdp << 16) + (pf << 8) + ps
    return f"{pri},{pgn},{src},{dst}"


def dump_in_canboat(canid: int, data: bytearray):
    """dump in canboat candump2analyzer"""
    # candump2analyzer format
    # "2024-07-29-12:55:17.133,7,126993,141,255,8,30,75,7c,cf,ff,ff,ff,ff"
    # "2024-07-29-12:48:36.815,4,129038,0,255,2,e4,ff"
    # "2024-07-29-12:48:36.815,3,129029,1,255,8,00,2b,c1,dc,4d,8e,3d,29"
    # "2024-08-08-01:19:24.597,5,130316,72,255,8,eb,00,01,04,8e,04,ff,ff"
    dtutc = datetime.datetime.now(datetime.timezone.utc)
    ts = f"{dtutc.strftime('%Y-%m-%d-%H:%M:%S')}.{int(dtutc.microsecond/1000):03d}"
    return f"{ts},{parse_can_id(canid)},{len(data)},{','.join(f'{x:02x}' for x in data)}"


def dump_in_candmp(canid: int, data: bytearray):
    """dump in candmp"""
    # candump format
    # "  can0  1DF0118D   [8]  30 75 7C CF FF FF FF FF"
    # "  can0  09F80101   [8]  4F 0E 76 18 A6 F7 2B D4"
    return f"  can0  {canid:08X}   [{len(data)}]  {' '.join(f'{x:02X}' for x in data)}"


def main():
    """main"""

    argparser = argparse.ArgumentParser(prog="canmonitor", description="canmonitor service logger")

    argparser.add_argument("-o", "--output", dest="output", help="output file")

    args = argparser.parse_args()

    if args.output:
        output_path = Path(args.output)
        output_dir = output_path.parent
        output_file = output_path.name
        output_file = RotatingFile(
            directory=output_dir,
            filename=output_file,
            max_file_size=100 * 1024 * 1024,
        )
        print(f"Print to file {output_file.filename_template}", file=sys.stderr)
    else:
        print("Print to stdout", file=sys.stderr)
        output_file = sys.stdout

    with can.Bus(interface="socketcan", channel="can0", bitrate=250000) as bus:
        for msg in bus:
            # output = dump_in_candmp(msg.arbitration_id, msg.data)
            output = dump_in_canboat(msg.arbitration_id, msg.data)
            output_file.write(f"{output}\n")


if __name__ == "__main__":
    main()
