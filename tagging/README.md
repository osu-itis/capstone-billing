# Overview
`tag_op.py` performs allows for the tagging/untagging of a virtual machine in vSphere. It internally uses the Python SDK for VMware vSphere. The script has currently been tested on the development environment. It is not yet runnable in production without further testing. Tagging information is stored in the yaml file.

On the development server, a VM called 'Test' has been created to test the tagging feature. Two tags are currently avaliable: chargeable and managed.

#### Usage:
Usage: `python3 tag_op.py <tag/untag> <tag_name> <vm_name>`
Ex: `python3 tag_op.py tag managed Test`

#### Configuration:
Please have a file called `settings.py` in this same directory with the following information.

```python
host = 'vctr-vd01.sig.oregonstate.edu'
user = '<replace with real username>'
password = '<replace with real password>'
port = 443 
url = 'https://{}/api'.format(host)
```
