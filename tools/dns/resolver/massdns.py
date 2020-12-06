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

class massdns(object):
    def __init__(self,targets,wordlist):
        self.targets = targets
        self.mainToolPath = wordlist.get('toolPath')

        #wordlist
        self.resolvers = self.mainToolPath + wordlist.get('massdnsResolvers')

        # output
        self.inputMDNS = "{tmpPath}{randomString}.txt".format(tmpPath=wordlist.get('tmpPath'),randomString=self.randomString())
        self.massdnsOutput = "{tmpPath}{randomString}.json".format(tmpPath=wordlist.get('tmpPath'),randomString=self.randomString())

    def randomString(self):
        k = ""
        for i in range(random.randint(10,20)):
            k += random.choice(string.printable.split('!')[0])
        return hashlib.md5(k.encode('utf-8')).hexdigest()

    def writeFile(self,tmp,targets):
        _file = open(tmp,'w+')
        for line in targets:
            _file.write('{line}\n'.format(line = line))
        _file.close()

    def runProcess(self):
        print('[ + ] Save all targets found...')
        self.writeFile(self.inputMDNS,self.targets)
        command = 'massdns -r {resolvers} -t A {targets} -o J -w {output}'.format(
            resolvers=self.resolvers,
            targets=self.inputMDNS,
            output=self.massdnsOutput
        )
        shell = subprocess.call(shlex.split(command),shell=False,stdout=subprocess.PIPE)
        print('[ + ] Finish resolved task..')

    def getOutput(self):
        output = []
        try:
            _file = readfile(self.massdnsOutput)
            for line in _file:
                line = ast.literal_eval(json.loads(json.dumps(line)))
                if line.get('status') == 'NOERROR' and line.get('data') != {}:
                    output.append(line.get('name'))
            os.remove(self.inputMDNS)
            os.remove(self.massdnsOutput)
            return output
        except Exception as err:
            print('[ + ] Error: %s'%(err))