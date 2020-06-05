*****scraper.py:*****

This script is dependent on pyvmomi and the vSphere automation SDK for python.
Currently, the script will only scan through the corvallis directory.

```python
corvallis_path = content.rootFolder.childEntity[0]
```

The script successfully grabs:

    - number of cpus

    - memory in MB

    - power state

    - guest name

    - department

    - fast/slow datastores

    - managed/chargeable tags

Since the indexes have not been tagged onto the VMs, the script cannot yet
grab the index. Instead, 'textidx' is used as a placeholder.

get\_tag\_association() builds the tags dictionary by default in the format

```python
{tag urn : [tag name, tag description ...}
```

So, when index tags are created, it can easily extendable in get\_info().
Grab the list of tag urns and use the global dictionary to translate.

```python
d = DynamicID(type='VirtualMachine', id=vm._GetMoId())
cat = None
for t in ta.list_attached_tags(d):
    if tags_dict[t][0] == 'Managed-VM':
        cat = 'managed'
        break
    elif tags_dict[t][0] == 'Chargeable-VM':
        cat = 'chargeable'
```

The script makes a few assumptions.

1. The department name is below the 'vm' folder, so we can backtrace to find
the department.
```python
pfolder = vm.parent
while pfolder.parent.name != 'vm':
    pfolder = pfolder.parent
```

2. If the datastore is fast storage if it has fast in its name.
```python
for device in vm.config.hardware.device:
    if type(device).__name__ == 'vim.vm.device.VirtualDisk':
        size = hrsize2b(device.deviceInfo.summary) / 2**30
        if 'fast' in device.backing.datastore.name:
            fast += size
        else:
            slow += size
```

*****db.py:*****

Currently, managed vms and chargeable vms are split up into tables. This may help
speed up querying for spreadsheet generation scripts. It is possible that this denormalization
may not be worth it, so these tables can be merged into one if need be.

The core logic is that we keep track of beginning and end times to record the lifespan of a VM.
A VM is considered new if any of the specs change (# cpus, memory, etc.). So, in the scraper script,
a hash is computed with all these specs as a unique identifier.

The insertion operation does an upsert. It updates the end time if the unique id is already seen, else
it inserts.

There exists an edge case where one vm can be double counted.

1. vm1 (id=1) | recorded into database at t=0
2. vm1 (id=2) | specifications of vm1 changed
3. vm1 (id=2) | time elapses
4. vm1 (id=1) | specifications of vm1 changed back

Now there are two entries for vm1 in the database. Since only start and end are kept track of, this
results in incorrect billing.

To fix this issue, we enforce a new entry every day by including a time in the hash. Doing this should
limit the damage of the rare edge case.

```python
timer = int(time.time() / (60*60*24))
state = f'{timer}|{vm.name}|{num_cpu}|{memory}|{fast}|{slow}|{power_state}|{guest_os}|{pfolder.name}|{idx}'
```

*****generate.py:*****

There is not much to generate.py at the moment. It is basic tabulation logic dumped into an excel spreadsheet.
Due to index not being pullable currently, it is not possible to get the spreadsheet into the FUPLOAD format.
However, finishing this should not take too much time. The generate file shows how to interact with the database.
