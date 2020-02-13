#!/usr/bin/env python3

import xlsxwriter
from db import *
from datetime import datetime

def add_chargeable(ws):
    row, col = 0, 0
    r = select_all('chargeable')

    header = ['Index', 'Dept', 'Name', 'Guest OS', 'Power Status', 
              'CPU', 'RAM (MB)', 'Fast Disk (GB)', 'Capacity (GB)',
              'Start', 'End']
    ws.write_row(row, col, tuple(header))
    row += 1

    for i in r:
        start = datetime.fromtimestamp(i[10]).strftime('%Y-%m-%d %H:%M:%S')
        end = datetime.fromtimestamp(i[11]).strftime('%Y-%m-%d %H:%M:%S')
        data = [i[9], i[8], i[1], i[7], i[6], i[2], i[3], i[4], i[5], start, end]
        
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
