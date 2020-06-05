#!/usr/bin/env python3

from pyVmomi import vim
from pyVim.connect import Disconnect, SmartConnect
from ssl import _create_unverified_context
import atexit 
from settings import host, port, user, password, url
from db import *
import hashlib
import time

import requests
from com.vmware.cis.tagging_client import (Tag, TagAssociation)
from com.vmware.cis_client import Session
from com.vmware.vapi.std_client import DynamicID
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.user_password import create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory

# dictionary of tag name to tag urn, built in get_tag_association
tags_dict = {}

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
    # specifically look at the corvallis path only
    corvallis_path = content.rootFolder.childEntity[0]
    container = content.viewManager.CreateContainerView(corvallis_path, [vim.VirtualMachine], True)
    return container.view

def get_tag_association():
    session = requests.Session()
    connector = get_requests_connector(session=session, url=url)
    stub_config = StubConfigurationFactory.new_std_configuration(connector)

    user_password_security_context = create_user_password_security_context(user, password)
    stub_config.connector.set_security_context(user_password_security_context)

    session_svc = Session(stub_config)
    session_id = session_svc.create()

    session_security_context = create_session_security_context(session_id)
    stub_config.connector.set_security_context(session_security_context)
    
    # Set up tag dictionary
    tag = Tag(stub_config)
    tag_list = tag.list()
    for t in tag_list:
        tag_model = tag.get(t) 
        tags_dict[tag_model.id] = [tag_model.name, tag_model.description]

    tag_association = TagAssociation(stub_config)
    return tag_association

def get_info():
    si = get_service_instance(host, user, password)
    vms = get_hosts(si)
    ta = get_tag_association()
    for vm in vms:
        # grab number of cpus, memory in MB, power state, and guest name
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

        # use placeholder index/chargeable flag until tagging is avaliable in production
        idx = 'testidx'

        # grab all the tags associated with the vm
        d = DynamicID(type='VirtualMachine', id=vm._GetMoId())
        cat = None
        for t in ta.list_attached_tags(d):
            if tags_dict[t][0] == 'Managed-VM':
                cat = 'managed'
                break
            elif tags_dict[t][0] == 'Chargeable-VM':
                cat = 'chargeable'
        

        timer = int(time.time() / (60*60*24))

        # hash the vm data for a unique identifier
        state = f'{timer}|{vm.name}|{num_cpu}|{memory}|{fast}|{slow}|{power_state}|{guest_os}|{pfolder.name}|{idx}'
        hashid = hashlib.md5(state.encode("utf-8")).hexdigest()

        yield cat, hashid, vm.name, num_cpu, memory, fast, slow, power_state, guest_os, pfolder.name, idx

def main():
    init_db()
    for i in get_info():
        t, *i = i

        print(t, i)
        # For the time being, just place everything untagged in chargeable...
        if not t:
            t = 'chargeable'

        insert_info(t, *i)

if __name__ == '__main__':
    main()
