# beets stuff
import os.path, sqlite3, re, filecmp

confpath=os.path.join(os.getenv("XDG_CONFIG_HOME",default=os.path.join(os.getenv("HOME", default="~"),"config")),"beets","config.yaml")

dirpath = None
dbpath = None
with open(confpath,'r') as f:
    # use re to parse YAML
    for line in f:
        m = re.match ("^directory:\s*(\S*)\s*$",line)
        if m:
            dirpath = os.path.expanduser(m.group(1))
        m = re.match ("^library:\s*(\S*)\s*$",line)
        if m:
            dbpath = os.path.expanduser(m.group(1))

if not dirpath:
    print ("directory not specified in config file")
    exit(1)

if not dbpath:
    print ("library not specified in config file")
    exit(1)

def connect():
    return sqlite3.connect(dbpath)
