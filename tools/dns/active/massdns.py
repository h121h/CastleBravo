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
        self.toolPath = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/tools/altdns.py'
        self.mainToolPath = wordlist.get('toolPath')
        # wordlist
        self.resolvers = self.mainToolPath + wordlist.get('massdnsResolvers')
        self.small = self.mainToolPath + wordlist.get('altdnsSmall') 
        self.medium = self.mainToolPath + wordlist.get('altdnsMedium')
        self.big = self.mainToolPath + wordlist.get('altdnsBig')
        # output
        self.altdnsInput = "{tmpPath}{randomString}.txt".format(tmpPath=wordlist.get('tmpPath'),randomString=self.randomString())
        self.altdnsOutput = "{tmpPath}{randomString}.txt".format(tmpPath=wordlist.get('tmpPath'),randomString=self.randomString())
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
        print('[ + ] Generate permutation altdns...')
        self.writeFile(self.altdnsInput,self.targets)
        command = 'python3 {altdnsPath} -i {altdnsInput} -o {altdnsOutput} -w {altdnsWordlist} -e -t 100'.format(
            altdnsPath=self.toolPath,
            altdnsInput=self.altdnsInput,
            altdnsOutput=self.altdnsOutput,
            altdnsWordlist=self.small
        )
        shell=subprocess.call(shlex.split(command),shell=False,stdout=subprocess.PIPE)
        # 
        print('[ + ] Altdns finished... masscan..')
        command = 'massdns -r {resolvers} -t A {targets} -o J -w {output}'.format(
            resolvers=self.resolvers,
            targets=self.altdnsOutput,
            output=self.massdnsOutput
        )
        shell = subprocess.call(shlex.split(command),shell=False,stdout=subprocess.PIPE)
        #
        print('[ + ] Finished massdns and altdns')

    def getOutput(self):
        output = []
        try:
            _file = readfile(self.massdnsOutput)
            for line in _file:
                line = json.loads(line)
                if line.get('status') == 'NOERROR':
                    output.append(line.get('name'))
        except Exception as err:
            print('[ + ] Error: %s'%(err))
        os.remove(self.altdnsInput)
        os.remove(self.altdnsOutput)
        os.remove(self.massdnsOutput)
        return output