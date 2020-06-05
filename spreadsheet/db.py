#!/usr/bin/env python3

import sqlite3
from sqlalchemy import *
import time

db_name = 'sqlite:///vminfo.db'
metadata = None
engine = None

def init_db():
    global metadata
    global engine

    engine = create_engine(db_name)
    metadata = MetaData()

    # splitting up chargeable and managed tables to speed up querying for spreadsheet generation
    # this denormalization may have negliable performance improvements (untested)
    # possible to merge these tables into one
    chargeable = Table('chargeable', metadata,
            Column('hashid', TEXT, primary_key=True),
            Column('name', TEXT, nullable=False),
            Column('num_cpu', INTEGER, nullable=False),
            Column('memory', INTEGER, nullable=False),
            Column('fast_disk', FLOAT, nullable=False),
            Column('normal_disk', FLOAT, nullable=False),
            Column('power_state', INTEGER, nullable=False),
            Column('guest_os', TEXT, nullable=False),
            Column('owner', TEXT, nullable=False),
            Column('index', TEXT, nullable=False),
            Column('start', INTEGER, nullable=False),
            Column('end', INTEGER, nullable=False))

    managed = Table('managed', metadata,
            Column('hashid', INTEGER, primary_key=True, autoincrement=True),
            Column('name', TEXT, nullable=False),
            Column('num_cpu', INTEGER, nullable=False),
            Column('memory', INTEGER, nullable=False),
            Column('fast_disk', FLOAT, nullable=False),
            Column('normal_disk', FLOAT, nullable=False),
            Column('power_state', INTEGER, nullable=False),
            Column('guest_os', TEXT, nullable=False),
            Column('owner', TEXT, nullable=False),
            Column('index', TEXT, nullable=False),
            Column('start', INTEGER, nullable=False),
            Column('end', INTEGER, nullable=False))

    metadata.create_all(engine, checkfirst=True)

def insert_info(table, hashid, name, num_cpu, memory, fast, slow, power_state, guest_os, owner, index):
    now = time.time()

    t = metadata.tables[table]

    # update last seen if the vm did not change
    qupdate = (t.update()
        .where(t.c.hashid == hashid)
        .values(end=now))

    # insert new entry if the vm changed (or is new)
    qinsert = t.insert().from_select(
        [
            t.c.hashid, t.c.name, t.c.num_cpu, t.c.memory,
            t.c.fast_disk, t.c.normal_disk, t.c.power_state,
            t.c.guest_os, t.c.owner, t.c.index, t.c.start,
            t.c.end
        ], select(
        [
            literal(hashid), literal(name), literal(num_cpu),
            literal(memory), literal(fast), literal(slow),
            literal(power_state), literal(guest_os), literal(owner),
            literal(index), literal(now), literal(now)
        ])
        .where(~exists().where(t.c.hashid == hashid))
    )

    conn = engine.connect()
    conn.execute(qupdate)
    conn.execute(qinsert)

def select_all(table):
    t = metadata.tables[table]
    qselect = t.select()
    conn = engine.connect()
    r = conn.execute(qselect)

    return r
