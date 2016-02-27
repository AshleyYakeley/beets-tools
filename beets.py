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
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    return conn

def clean(s):
    return s.replace(":","_").replace("?","_").replace("/","_")

class Album:
    def __init__(self,conn,id):
        (row,) = conn.execute("SELECT * FROM albums WHERE id=?",[id])
        self.row = row
        self.row_id = id
        self.guid = row["mb_albumid"]
        self.artist_name = row["albumartist"]
        self.album_name = row["album"]
        self.name = self.artist_name+" - "+self.album_name
        self.desc = str(id)+": "+self.name

    def clean_artist_name(self):
        if self.artist_name == "Various Artists":
            return "Compilations"
        else:
            return clean(self.artist_name)

    def item_count(self,conn):
        ((count,),) = conn.execute("SELECT COUNT(*) FROM items WHERE album_id = ?",[self.row_id])
        return count

    def items(self,conn):
        return conn.execute("SELECT * FROM items WHERE album_id = ? ORDER BY track ASC",[self.row_id])

    def paths(self):
        artistpath = self.clean_artist_name()
        albumpath = clean(self.album_name)
    
        def test_path(extra,level):
            relpath = os.path.join(artistpath,albumpath + extra)
            abspath = os.path.join(dirpath,relpath)
            if os.path.isdir(abspath):
                return (relpath,abspath,extra,level)
            else:
                return None
        
        paths = test_path(" " + str(self.row_id),3)
        if paths is not None:
            return paths
        paths = test_path(" [" + str(self.row["year"]) +"]",2)
        if paths is not None:
            return paths
        paths = test_path(" [" + self.row["label"] +"]",1)
        if paths is not None:
            return paths
        paths = test_path("",0)
        if paths is not None:
            return paths
        return None

