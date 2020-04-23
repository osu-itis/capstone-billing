#!/usr/bin/env python3

import ssl
import time
import sys
import requests
from com.vmware.cis.tagging_client import (Tag, TagAssociation)
from com.vmware.cis_client import Session
from com.vmware.vapi.std_client import DynamicID
from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.user_password import create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from settings import host, user, password, port, url

tags = {
        'managed': 'urn:vmomi:InventoryServiceTag:3a2841b7-495c-4b72-a1e9-9654571ba9f7:GLOBAL',
        'chargeable' : 'urn:vmomi:InventoryServiceTag:d66e1dfc-3791-43c2-a336-0b7abd193241:GLOBAL'
}

def get_vm_id(name):
    """Find vm id by given name using pyVmomi."""
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        sslContext = ssl._create_unverified_context()

    si = SmartConnect(host=host, port=port, user=user, pwd=password, sslContext=sslContext)
    content = si.content
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True
    vmView = content.viewManager.CreateContainerView(container, viewType, recursive)
    vms = vmView.view
    for vm in vms:
        if vm.name == name:
            return vm._GetMoId()
    raise Exception('VM with name {} could not be found'.format(name))

def get_tag_association():
    session = requests.Session()
    session.verify = False
    connector = get_requests_connector(session=session, url=url)
    stub_config = StubConfigurationFactory.new_std_configuration(connector)

    user_password_security_context = create_user_password_security_context(user, password)
    stub_config.connector.set_security_context(user_password_security_context)

    session_svc = Session(stub_config)
    session_id = session_svc.create()

    session_security_context = create_session_security_context(session_id)
    stub_config.connector.set_security_context(session_security_context)

    tag_association = TagAssociation(stub_config)
    return tag_association

def tag(vm_name, tag_op, tag_id):
    # get VM
    vm_moid = get_vm_id(vm_name)
    assert vm_moid is not None

    # get tag association
    tag_association = get_tag_association()

    if tag_op == "tag":
        dynamic_id = DynamicID(type='VirtualMachine', id=vm_moid)
        tag_association.attach(tag_id=tag_id, object_id=dynamic_id)
        for tag_id in tag_association.list_attached_tags(dynamic_id):
            if tag_id == tag_id:
                tag_attached = True
                break
        assert tag_attached
    elif tag_op == "untag":
        dynamic_id = DynamicID(type='VirtualMachine', id=vm_moid)
        tag_association.detach(tag_id=tag_id, object_id=dynamic_id)
        for tag_id in tag_association.list_attached_tags(dynamic_id):
            if tag_id == tag_id:
                tag_attached = True
                break
        assert tag_attached

def main():
    if len(sys.argv) != 4:
        print('Usage: ./tag_op <tag/untag> <tag_name> <vm_name>')
        sys.exit()

    tag_op = sys.argv[1]
    tag_id = tags[sys.argv[2]]
    vm_name = sys.argv[3]

    tag(vm_name, tag_op, tag_id)
    print('Success.')

if __name__ == '__main__':
    main()
