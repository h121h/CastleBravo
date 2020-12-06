# CastleBravo V2 - BugBounty Automation
# by @m4ll0k - github.com/m4ll0k

import shlex
import subprocess
from libs.readfile import readfile
import os 


class subfinder(object):
    def __init__(self,target,tmpPath):
        self.target = target 
        self.tmpPath = tmpPath + '.txt'
        self.subfinderConfigPath = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/tools/config.yaml'
        self.subfinderToolPath   = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/tool/subfinder'
    
    def runProccess(self):
        print('[ - ] Running subfinder...')
        command = '{toolPath} -d {target} -config {configPath} -o {tmpPath}'.format(
            toolPath=self.subfinderToolPath,
            target=self.target,
            configPath=self.subfinderConfigPath,
            tmpPath=self.tmpPath
        )
        shell = subprocess.call(shlex.split(command),shell=False,stdout=subprocess.PIPE)
        print('[ I ] Output: '+self.tmpPath)

    def getOutput(self):
        try:
            return readfile(self.tmpPath)
        except Exception as err:
            print('[ E ] ERROR: ' + str(err))