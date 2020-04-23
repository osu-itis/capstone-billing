# capstone-billing

Set up environment:
```
$ sudo apt-get install python3-venv
$ python3 -m venv billing-env
$ source billing-env/bin/activate
$ pip install -r requirements.txt
```
For Tagging:

Upgrade to the latest pip and setuptools.
```
$ sudo pip install --upgrade pip setuptools
$ sudo pip install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git
$ python3 Tag_OP.py tag tagID(Unknown as of now) Test(test VM)
```
