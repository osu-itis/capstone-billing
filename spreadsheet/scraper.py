#!/usr/bin/env python3

from pyVmomi import vim
from pyVim.connect import Disconnect, SmartConnect
from ssl import _create_unverified_context
import atexit 
from settings import server, port, user, password
from db import *
import hashlib

def hrsize2b(size):
    units = {'B': 1, 'KB': 2**10, 'MB': 2**20, 'GB': 2**30, 'TB': 2**40}
    number, unit = [string.strip() for string in size.split()]
    return float(number.replace(',', ''))*units[unit]

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
    corvallis_path = content.rootFolder.childEntity[0]
    container = content.viewManager.CreateContainerView(corvallis_path, [vim.VirtualMachine], True)
    return container.view

def get_info():
    si = get_service_instance(server, user, password)
    vms = get_hosts(si)
    for vm in vms:
        num_cpu = vm.config.hardware.numCPU
        memory = vm.config.hardware.memoryMB
        power_state = 1 if 'On' in vm.runtime.powerState else 0
        guest_os = vm.summary.config.guestFullName

        # grab parent folder == dept
        pfolder = vm.parent
        while pfolder.parent.name != 'vm':
            pfolder = pfolder.parent

        # grab storage information for fast/normal datastores
        fast, slow = 0, 0
        for device in vm.config.hardware.device:
            if type(device).__name__ == 'vim.vm.device.VirtualDisk':
                size = hrsize2b(device.deviceInfo.summary) / 2**30
                if 'fast' in device.backing.datastore.name:
                    fast += size
                else:
                    slow += size
        fast, slow = round(fast, 2), round(slow, 2)

        # todo, grab index + managed from tags
        # perhaps store in extra config?
        # see: https://github.com/virtdevninja/pyvmomi-community-samples/commit/0dbbb1dd28045e8406c70c9830d08d39b55406a7

        '''
        # or attributes
        f = si.content.customFieldsManager.field
        for k, v in [(x.name, v.value) for x in f for v in vm.customValue if x.key == v.key]:
           print("Name: %s\nValue: %s" % (k, v))
        '''
        idx = 'testidx'

        state = f'{vm.name}|{num_cpu}|{memory}|{fast}|{slow}|{power_state}|{guest_os}|{pfolder.name}|{idx}'
        hashid = hashlib.md5(state.encode("utf-8")).hexdigest()

        yield 0, hashid, vm.name, num_cpu, memory, fast, slow, power_state, guest_os, pfolder.name, idx

def main():
    init_db()
    for i in get_info():
        t, *i = i
        t = 'chargeable' if t == 0 else 'managed'
        insert_info(t, *i)

if __name__ == '__main__':
    main()
