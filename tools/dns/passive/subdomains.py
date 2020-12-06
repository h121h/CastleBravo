# CastleBravo V2 - BugBounty Automation
# by @m4ll0k - github.com/m4ll0k

import shlex
import subprocess
from libs.readfile import readfile
import os 


class subdomains(object):
    def __init__(self,target,tmpPath):
        self.target = target 
        self.tmpPath = tmpPath + '.txt'
        self.subdomainsToolPath   = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/tool/subdomain.sh'
    
    def runProccess(self):
        print('[ - ] Running subdomain.sh...')
        command = 'bash {toolPath} {target}'.format(
            toolPath=self.subdomainsToolPath,
            target=self.target
        )
        shell = subprocess.call(shlex.split(command),shell=False,stdout=open(self.tmpPath,'w+'))
        print('[ I ] Output: '+self.tmpPath)

    def getOutput(self):
        try:
            return readfile(self.tmpPath)
        except Exception as err:
            print('[ E ] ERROR: ' + str(err))