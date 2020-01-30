#!/usr/bin/env python3

from pyVmomi import vim
from pyVim.connect import Disconnect, SmartConnect
from ssl import _create_unverified_context
import atexit
from settings import server, port, user, password
from db import *

def get_service_instance(host, user, pwd):
    try:
        sslContext = _create_unverified_context()
        si = SmartConnect(host=host, port=port, user=user, pwd=pwd, sslContext=sslContext)
    except Exception as e:
        raise SystemExit
    atexit.register(Disconnect, si)
    return si

def get_hosts(conn):
    content = conn.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    return container.view

def get_info():
    si = get_service_instance(server, user, password)
    vms = get_hosts(si)
    for vm in vms:
        num_cpu = vm.config.hardware.numCPU
        memory = vm.config.hardware.memoryMB
        disk_size = vm.summary.storage.committed + vm.summary.storage.uncommitted
        power_state = 1 if 'On' in vm.runtime.powerState else 0
        guest_os = vm.summary.config.guestFullName

        yield vm.name, num_cpu, memory, disk_size, power_state, guest_os, 'tempowner'

def main():
    init_db()
    for i in get_info():
        insert_info('chargeable', *i)

if __name__ == '__main__':
    main()
