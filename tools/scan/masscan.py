# CastleBravo V2 - BugBounty Automation
# by @m4ll0k - github.com/m4ll0k

import re 
import subprocess
import shlex 
import os 
import random
import string
import ast
import json
import hashlib

#custom
from libs.readfile import readfile

class masscan(object):
    def __init__(self,targets):
        self.targets = targets
        # output 
        self.outputMascan = "/tmp/{randomString}.json".format(randomString=self.randomString())

    def randomString(self):
        k = ""
        for i in range(random.randint(10,20)):
            k += random.choice(string.printable.split('!')[0])
        return hashlib.md5(k.encode('utf-8')).hexdigest()

    def runProcess(self):
        print('[ + ] Starting masscan for %s..'%self.targets)
        command = 'masscan -Pn  --max-rate 100000 -p0-65535 -sS -oJ {output} {targets}'.format(
            targets=self.targets,
            output=self.outputMascan
        )
        shell = subprocess.call(shlex.split(command),shell=False,stdout=subprocess.PIPE)
        print('[ + ] Finish port scanning..')

    def getOutput(self):
        output = ""
        try:
            _file = readfile(self.outputMascan)
            _file = "".join(_file).replace(' ','')
            for line in _file.split('},'):
                if not line.endswith(']}'):
                    line = line + '}'
                    i = json.loads(line)
                    if i.get('ip') and i.get('ports'):
                         port = str(i.get('ports')[0].get('port')) + '/' + i.get('ports')[0].get('proto')
                         output += "{port};".format(port=port)
                else:
                    i = json.loads(line) 
                    if i.get('ip') and i.get('ports'):
                        port = str(i.get('ports')[0].get('port')) + '/' + i.get('ports')[0].get('proto')
                        output += "{port};".format(port=port)
            os.remove(self.massdnsOutput)
            return output
        except Exception as err:
            print('[ + ] Error: %s'%(err))