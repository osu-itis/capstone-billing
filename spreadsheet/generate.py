#!/usr/bin/env python3

import xlsxwriter
from db import *
from datetime import datetime

vCPU = 38
RAM = 28
OSDisk = 1.5
CapDisk = 0.09
WinLic = 24
SvrMgmt = 91

Month = 30 * 24 * 60 * 60

# 0 hashid
# 1 name
# 2 num_cpu
# 3 memory
# 4 fast_disk
# 5 normal_disk
# 6 power_state
# 7 guest_os
# 8 owner
# 9 index
# 10 start
# 11 end
def tabulate_row(row):
    total = 0
    total += row[2] * vCPU
    total += row[3] * RAM
    total += row[4] * OSDisk
    total += row[5] * CapDisk

    if 'windows' in row[7].lower():
        total += WinLic

    diff = row[11] - row[10] + (15*60)
    total *= (diff / Month)

    return total

def add_chargeable(ws):
    row, col = 0, 0
    r = list(select_all('chargeable'))
    r = sorted(r, key=lambda x: x[8])

    header = ['Index', 'Dept', 'Name', 'Guest OS', 'Power Status', 
              'CPU', 'RAM (MB)', 'Fast Disk (GB)', 'Capacity (GB)',
              'Start', 'End', 'VM Cost']

    ws.write_row(row, col, tuple(header))
    row += 1

    for i in r:
        start = datetime.fromtimestamp(i[10]).strftime('%Y-%m-%d %H:%M:%S')
        end = datetime.fromtimestamp(i[11]).strftime('%Y-%m-%d %H:%M:%S')
        cost = tabulate_row(i)

        data = [i[9], i[8], i[1], i[7], i[6], i[2], i[3], i[4], i[5], start, end, cost/100]
        
        ws.write_row(row, col, tuple(data))
        row += 1


def main():
    wb = xlsxwriter.Workbook('test.xlsx')
    ws = wb.add_worksheet()

    init_db()
    add_chargeable(ws)
    wb.close()


if __name__ == '__main__':
    main()
