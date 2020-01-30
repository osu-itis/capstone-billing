#!/usr/bin/env python3

import sqlite3
from sqlalchemy import *

db_name = 'sqlite:///vminfo.db'
metadata = None
engine = None

def init_db():
    global metadata
    global engine

    engine = create_engine(db_name)
    metadata = MetaData()
    chargeable = Table('chargeable', metadata,
            Column('id', INTEGER, primary_key=True, autoincrement=True),
            Column('name', TEXT, nullable=False),
            Column('num_cpu', INTEGER, nullable=False),
            Column('memory', INTEGER, nullable=False),
            Column('disk_size', INTEGER, nullable=False),
            Column('power_state', INTEGER, nullable=False),
            Column('guest_os', TEXT, nullable=False),
            Column('owner', TEXT, nullable=False))

    metadata.create_all(engine, checkfirst=True)

def insert_info(table, name, num_cpu, memory, disk_size, power_state, guest_os, owner):
    inq = metadata.tables[table].insert().values(
        name=name,
        num_cpu=num_cpu,
        memory=memory,
        disk_size=disk_size,
        power_state=power_state,
        guest_os=guest_os,
        owner=owner)
    conn = engine.connect()
    conn.execute(inq)
