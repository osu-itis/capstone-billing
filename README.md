# CS75: Capstone Billing Project

This is the main repository for the capstone billing project.
The repository is divided into two main sections: a spreadsheet scraping/generation portion, and a tagging portion.

spreadsheet/\* consists of scripts that pull data from vSphere and generates a spreadsheet from it. This operates on the production servers currently.
tagging/\* consists of scripts that push tags to virtual machines in order to supply extra data to the pulling process. This operates on the development servers currently.

Each portion can be tested individually. Nagivate to the directories for more information.


#### Environment setup:
```
$ sudo apt-get install python3-venv
$ python3 -m venv billing-env
$ source billing-env/bin/activate
$ pip install -r requirements.txt
```

#### Notes:
**These scripts will only work on the OSU network. If off-campus, please connect to VPN.**
