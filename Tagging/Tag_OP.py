#!/usr/bin/python

import ssl
import time
import sys
import requests
from com.vmware.cis.tagging_client import (
    Tag, TagAssociation)
from com.vmware.cis_client import Session
from com.vmware.vapi.std_client import DynamicID
from pyVim import connect
from pyVmomi import vim
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory


tag_op = sys.argv[1]
tag_id = sys.argv[2]
vm_name = sys.argv[3]

vcenter_server = 'vctr-vd01.sig.oregonstate.edu'
url = 'https://{}/api'.format(vcenter_server)
vcenter_username = 'sig_capstone_pu@onid.oregonstate.edu' #User with enough privilege
vcenter_password = 'pu{senior_capstone_75}'
vcenter_cluster_name = 'apollo'

def get_vm_id(name):
    """Find vm id by given name using pyVmomi."""
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()

    si = connect.Connect(host=vcenter_server, user=vcenter_username, pwd=vcenter_password,
                         sslContext=context)
    content = si.content
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True
    vmView = content.viewManager.CreateContainerView(container,
                                                     viewType,
                                                     recursive)
    vms = vmView.view
    for vm in vms:
        if vm.name == name:
            return vm._GetMoId()
    raise Exception('VM with name {} could not be found'.format(name))



session = requests.Session()
session.verify = False
connector = get_requests_connector(session=session, url=url)
stub_config = StubConfigurationFactory.new_std_configuration(connector)

user_password_security_context = create_user_password_security_context(vcenter_username, vcenter_password)
stub_config.connector.set_security_context(user_password_security_context)

session_svc = Session(stub_config)
session_id = session_svc.create()

session_security_context = create_session_security_context(session_id)
stub_config.connector.set_security_context(session_security_context)

tag_association = TagAssociation(stub_config)

print('finding the vm {0}'.format(vm_name))
vm_moid = get_vm_id(vm_name)
assert vm_moid is not None
print('Found vm:{0} mo_id:{1}'.format('vAPISDKVM', vm_moid))

if tag_op == "tag":
    print('Tagging the vm {0}...'.format(vm_moid))
    dynamic_id = DynamicID(type='VirtualMachine', id=vm_moid)
    tag_association.attach(tag_id=tag_id, object_id=dynamic_id)
    for tag_id in tag_association.list_attached_tags(dynamic_id):
        if tag_id == tag_id:
            tag_attached = True
            break
    assert tag_attached
    print('Tagged vm: {0}'.format(vm_moid))
elif tag_op == "untag":
    print('Tagging the vm {0}...'.format(vm_moid))
    dynamic_id = DynamicID(type='VirtualMachine', id=vm_moid)
    tag_association.detach(tag_id=tag_id, object_id=dynamic_id)
    for tag_id in tag_association.list_attached_tags(dynamic_id):
        if tag_id == tag_id:
            tag_attached = True
            break
    assert tag_attached
    print('Tagged vm: {0}'.format(vm_moid))
