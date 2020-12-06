# CastleBravo V2 - BugBounty Automation
# by @m4ll0k - github.com/m4ll0k

import shlex
import subprocess
from libs.readfile import readfile
import os 


class amass(object):
    def __init__(self,target,tmpPath):
        self.target = target 
        self.tmpPath = tmpPath + '.txt'
        self.amassConfigPath = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/tools/config.ini'
        self.amassToolPath   = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/tool/amass'
    
    def runProccess(self):
        print('[ - ] Running amass...')
        command = '{toolPath} enum -passive -silent -d {target} -config {configPath} -o {tmpPath}'.format(
            toolPath=self.amassToolPath,
            target=self.target,
            configPath=self.amassConfigPath,
            tmpPath=self.tmpPath
        )
        shell = subprocess.call(shlex.split(command),shell=False,stdout=subprocess.PIPE)
        print('[ I ] Output: '+self.tmpPath)

    def getOutput(self):
        try:
            return readfile(self.tmpPath)
        except Exception as err:
            print('[ E ] ERROR: ' + str(err))