# Overview
`scraper.py` scrapes all the necessary billing information from production VMs and stores it into a SQLite3 database.

`generate.py` generates a billing spreadsheet using the scraped information.

The scripts currently operate on the production servers. (It does not mutate data, meaning it is safe to run without
testing.) When deployed, scraper.py will be ran in 15 minute increments. generate.py will be ran monthly/quarterly
depending on whether it is managed or chargeable.

#### Usage:
`python3 scraper.py`

`python3 generate.py`

#### Configuration:
Please have a file called `settings.py` in this same directory with the following information.

```python
host = 'vcenter-vp01.sig.oregonstate.edu'
user = '<replace with real username>'
password = '<replace with real password>'
port = 443
url = 'https://{}/api'.format(host)
```
