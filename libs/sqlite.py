# CastleBravo V2 - BugBounty Automation
# by @m4ll0k - github.com/m4ll0k

import sqlite3
import time


class handleDB(object):
    def __init__(self):
        #self.db_path = dbPath
        self.connect = sqlite3.connect(':memory:')
        self.sqlite = self.connect.cursor()
    
    def executeQuery(self,query):
        x =  self.sqlite.execute(query)
        self.save()
        return x
    
    def save(self):
        self.connect.commit()
    
    def close(self):
        self.connect.close()

