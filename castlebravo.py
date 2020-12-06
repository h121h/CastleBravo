# CastleBravo V2  - BugBounty Automation
# by @m4ll0k - github.com/m4ll0k

# parts of full version

import re
import sys 
import os 
import time
import json
import hashlib
import sqlite3
import random
import string
import requests 

import dns.resolver
import dns.exception

# part 
from urllib.parse import *
from datetime import datetime, timedelta

# custom libs
from libs.readfile import readfile 
from libs.sqlite import handleDB

class castleBravoV2(handleDB):
    ''' castlebravo main '''
    lastTimeConfig = None
    firtsTime = True
    configName = "config.json"
    def __init__(self):
        self.setSetup() # setup
        # generate random db path
        #self.currentDBPath = self.config.get('tmpPath') + self.getRandomString() + self.config.get('dbExt')
        handleDB.__init__(self)
        # global vars 
        self.telegramRequest('Starting CastleBravoV2...')
        self.inscope  = self.config.get('inScope') 
        self.outscope = self.config.get('outScope')
    
    def getmd5Hash(self,_str):
        return hashlib.md5(_str.encode('utf-8')).hexdigest()
    
    def getRandomString(self):
        k = ""
        for i in range(random.randint(10,20)):
            k += random.choice(string.printable.split('!')[0])
        return hashlib.md5(k.encode('utf-8')).hexdigest()

    def getPath(self):
        '''
        + get tool path and split end of path   
        '''
        path = os.path.abspath(__file__).split('/')[:-1]
        self.toolPath = "/".join(path)
    
    def getTimeandDate(self):
        return time.strftime(r'%H:%M:%S - %d:%m:%Y')
    
    def getTime(self):
        return datetime.now().strftime(r'%H:%M:%S')
    
    def getDate(self):
        return datetime.now().strftime(r'%d:%m:%Y')

    def getAbsPath(self):
        '''
        + get absolute path
        '''
        self.absPath = os.path.abspath(__file__) 

    def setSetup(self):
        self.getPath()
        self.getAbsPath()
        self.configParser()
        self.lastTimeConfig = os.stat(self.configPath).st_mtime # config 
    
    def configReload(self):
        content = readfile(self.configPath)
        self.config = json.loads("\n".join(content) if content != [] else '{}')
        self.__init__()

    def configParser(self):
        self.configPath = self.toolPath + '/{path}'.format(path=castleBravoV2.configName)
        content = readfile(self.configPath)
        self.config = json.loads("\n".join(content) if content != [] else '{}')
    
    def sqliteSetup(self,targetName):
        '''
        + create a sqlite3 db for single target and save it in db path 
        '''
        self.dbName = targetName.replace('.','_').replace('-','_') + '.db'
        self.dbTableName = targetName.replace('.','_').replace('-','_')
        self.currentDBPath = self.toolPath + self.config.get('dbPath') + self.dbName
        sqlite = sqlite3.connect(self.toolPath + self.config.get('dbPath') + '{name}'.format(name=self.dbName))
        sqlite.cursor()
        sqlite.commit()
        sqlite.close()
    
    def nextTime(self):
        # scan target after 30 days for leatest scan
        _nextTime = datetime.now() + timedelta(days=30)
        return _nextTime.strftime(r'%d:%m:%Y')

    def configChange(self):
        current = os.stat(self.configPath).st_mtime
        if self.firtsTime is True or current != self.lastTimeConfig:
            self.lastTimeConfig = current
            self.firtsTime = False
            return True 
        return False
    
    def startProcess(self):
        k = {}
        while True:
            if self.inscope != []:
                if self.configChange():
                    self.configReload()
                for root in self.inscope:
                    self.root = root
                    if k.get(root) is None:
                        k[root] = {'first':False}
                    if k.get(root).get('first') is False:
                        k[root] = {'first':True}
                    elif k.get(root).get('first') is True:
                        next_ = self.executeQuery('SELECT * FROM {tableName}.nextscan'.format(tableName=self.dbTableName)).fetchone()[0]
                        if self.getDate() > next_:
                            continue
                        elif self.getDate() == next_:
                            pass
                        else:
                            continue
                    self.target = root
                    self.sqliteSetup(root)
                    # create a table for new domain
                    # exampel: uber.com -> table -> uber_com
                    self.executeQuery('''ATTACH "{tableName}" AS {tableName2}'''.format(tableName=self.currentDBPath,tableName2=self.dbTableName))
                    self.executeQuery('''CREATE TABLE IF NOT EXISTS {tableName}.date(Date TEXT)'''.format(tableName=self.dbTableName))
                    self.executeQuery('''CREATE TABLE IF NOT EXISTS {tableName}.time(Date TEXT)'''.format(tableName=self.dbTableName))
                    self.executeQuery('''CREATE TABLE IF NOT EXISTS {tableName}.nextscan(Date TEXT)'''.format(tableName=self.dbTableName))
                    self.executeQuery('''CREATE TABLE IF NOT EXISTS {tableName}.subdomains(subDomain TEXT,ip TEXT,addAt TEXT,scanAt TEXT,resolved,isNew,telegramNotification,nmapPorts TEXT,masscanPorts TEXT,md5Hash TEXT)'''.format(tableName=self.dbTableName))
                    # insert 
                    self.executeQuery('''INSERT INTO {tableName}.date VALUES("{time}")'''.format(tableName=self.dbTableName,time=self.getDate()))
                    self.executeQuery('''INSERT INTO {tableName}.time VALUES("{time}")'''.format(tableName=self.dbTableName,time=self.getTime()))
                    # next scan for the domain, 30 days
                    self.executeQuery('''INSERT INTO {tableName}.nextscan VALUES("{time}")'''.format(tableName=self.dbTableName,time=self.nextTime()))
                    # telegram
                    self.telegramRequest('[%(time)s - %(date)s] Scanning "%(root)s"'%({"root":root,
                        "time":self.executeQuery('SELECT * FROM {tableName}.time'.format(tableName=self.dbTableName)).fetchone()[0],
                        "date":self.executeQuery('SELECT * FROM {tableName}.date'.format(tableName=self.dbTableName)).fetchone()[0]
                    }))
                    ## 
                    subdomains = self.subdomainProcess(root)
                    self.telegramRequest('Finish subdomain enumeration..')
                    self.telegramRequest('Found {subs} domains'.format(subs=len(subdomains)))
                    # -- port scanning 
                    #self.portScanProcess(subdomains)
                    # -- get http/s --
                    # httpSubdomains = self.getHttp(subdomains)
                    # -- dir bruteforce --- 
                    # self.bruteForceProcess(httpSubdomains)
                    # ... etc
    
    def telegramNotification(self):
        pass

    def saveOutput(self):
        pass

    def getIP(self,target):
        # ip1 ip2 ip4 
        ips = ""
        try:
            answer = dns.resolver.query(target,'A')
            for i in answer:
                if ips == "":
                    ips += i 
                else:
                    ips += " {ip}".format(ip=i)
            return ips
        except dns.exception.DNSException:
            return ""

    def inOutofScope(self,target):
        if self.outscope != []:
            for i in self.outscope:
                if target.find(i) >= 0:
                    return True 
        return False

    def getDBCount(self):
        return self.executeQuery('SELECT COUNT(*) FROM {tableName}.subdomains'.format(tableName=self.dbTableName)).fetchone()[0]

    def telegramRequest(self,content):
        r = requests.get('https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}'.format(
            token=self.config.get('keys').get('telegramToken'),
            chat_id=self.config.get('keys').get('chatId'),
            text=content
        ))
    
    def getHttp(self,subs):
        pass

    def bruteForceProcess(self,subs):
        pass

    def portScanProcess(self,subs):
        self.telegramRequest('Starting ports scanning..')
        from tools.scan import masscan
        for sub in subs:
            masscanProcess = masscan.masscan(self.getIP(sub))
            masscanProcess.runProcess()
            _ports = masscanProcess.getOutput()
            # put results in db 
            if _ports != "":
                rowid = self.executeQuery('''SELECT rowid FROM {tableName}.subdomains WHERE subDomain == "{sub}"'''.format(tableName=self.dbTableName,sub=sub)).fetchone()
                if type(rowid) is tuple:
                    rowid = rowid[0]
                    self.executeQuery('''UPDATE {tableName}.subdomains SET masscanPorts = "{ports}" WHERE rowid == {rowid}'''.format(tableName=self.dbTableName,ports=_ports,rowid=rowid))
                    self.executeQuery('''UPDATE {tableName}.subdomains SET ip = "{ips}" WHERE rowid == {rowid}'''.format(tableName=self.dbTableName,ips=self.getIP(sub),rowid=rowid))
    
    def subdomainProcess(self,root):
        root = [root]
        t_passive = self.passiveDNS(root) 
        self.telegramRequest('[%s] Finish passive DNS'%self.getTime())
        t_active = self.activeDNS(root)
        self.telegramRequest('[%s] Finish active DNS'%self.getTime())
        # join active and passive dns enumeration to targets
        # pass it again (all targets) to active process 
        # finally to resolver
        _targets = []
        for i in (t_passive,t_active):
            for k in i:
                if k.startswith('.'):
                    k = k[1:]
                if re.findall('[\.]{root}$'.format(root=self.root),k,re.I) == [] or self.inOutofScope(k):
                    continue
                if k not in _targets:
                    # subDomain,ip,addAt,scanAt,resolved,isNew,telegramNotification,nmapPorts,masscanPorts,md5Hash
                    self.executeQuery('''INSERT INTO {tableName}.subdomains VALUES ("{subDomain}",NULL,"{addAt}",NULL,0,1,0,NULL,NULL,"{md5Hash}")'''.format(
                            subDomain = k,
                            tableName = self.dbTableName,
                            addAt = self.getTime(),
                            md5Hash = self.getmd5Hash(k)
                        ))
                    _targets.append(k)
        self.telegramRequest('Found %d domains for %s'%(len(_targets),self.target))
        t_active_v2 = self.activeDNS(_targets)
        for i in t_active_v2:
            if i.startswith('.'):
                i = i[1:]
            if re.findall('[\.]{root}$'.format(root=self.root),k,re.I) == [] or self.inOutofScope(k):
                continue
            if i not in _targets:
                # subDomain,ip,addAt,scanAt,resolved,isNew,telegramNotification,nmapPorts,masscanPorts,md5Hash
                self.executeQuery('''INSERT INTO {tableName}.subdomains VALUES ("{subDomain}",NULL,"{addAt}",NULL,0,1,0,NULL,NULL,"{md5Hash}")'''.format(
                    subDomain = i,
                    tableName = self.dbTableName,
                    addAt = self.getTime(),
                    md5Hash = self.getmd5Hash(i)
                ))
                _targets.append(i)
        self.telegramRequest('Finish phase two with active DNS..')
        self.telegramRequest('Found %d domains for %s'%(len(_targets),self.target))
        self.telegramRequest('Start resolver..')

        # resolver with massdns 

        resolvedEnd = self.resolverProcess(_targets)
        for i in resolvedEnd:
            if i.endswith('.'):
                i = i[:-1]
            rowid = self.executeQuery('''SELECT rowid FROM {tableName}.subdomains WHERE subDomain == "{sub}"'''.format(tableName=self.dbTableName,sub=i)).fetchone()
            if type(rowid) is tuple:
                rowid = rowid[0]
                self.executeQuery('''UPDATE {tableName}.subdomains SET resolved = 1 WHERE rowid == {rowid}'''.format(tableName=self.dbTableName,rowid=rowid))
            elif rowid is None:
                self.executeQuery('''INSERT INTO {tableName}.subdomains VALUES ("{subDomain}",NULL,"{addAt}",NULL,{resolved},1,0,NULL,NULL,"{md5Hash}")'''.format(subDomain =i,resolved=1,tableName = self.dbTableName,addAt = self.getTime(),md5Hash = self.getmd5Hash(i)))
        return resolvedEnd

    def passiveDNS(self,domains):

        ext = '.txt'

        from tools.dns.passive import amass
        from tools.dns.passive import crobat
        from tools.dns.passive import assetfinder
        from tools.dns.passive import github
        from tools.dns.passive import subdomains
        from tools.dns.passive import subfinder

        passive = []
        for domain in domains:
            # amass
            randomTmpPath = self.config.get('tmpPath') + self.getRandomString()
            subDomains = amass.amass(domain,randomTmpPath)
            subDomains.runProccess()
            _subDomains = subDomains.getOutput()
            if _subDomains:
                for sub in _subDomains:
                    if sub not in passive:
                        passive.append(sub)
            # remove tmp file, after get content 
            os.remove(randomTmpPath+ext)
            # crobat
            randomTmpPath = self.config.get('tmpPath') + self.getRandomString()
            subDomains = crobat.crobat(domain,randomTmpPath)
            subDomains.runProccess()
            _subDomains = subDomains.getOutput()
            if _subDomains:
                for sub in _subDomains:
                    if sub not in passive:
                        passive.append(sub)
            # remove tmp file, after get content 
            os.remove(randomTmpPath+ext)
            # assetfinder
            randomTmpPath = self.config.get('tmpPath') + self.getRandomString()
            subDomains = assetfinder.assetfinder(domain,randomTmpPath)
            subDomains.runProccess()
            _subDomains = subDomains.getOutput()
            if _subDomains:
                for sub in _subDomains:
                    if sub not in passive:
                        passive.append(sub)
            # remove tmp file, after get content
            os.remove(randomTmpPath+ext)
            # github
            randomTmpPath = self.config.get('tmpPath') + self.getRandomString()
            subDomains = github.github(domain,randomTmpPath)
            subDomains.runProccess()
            _subDomains = subDomains.getOutput()
            if _subDomains:
                for sub in _subDomains:
                    if sub not in passive:
                        passive.append(sub)
            # remove tmp file, after get content
            os.remove(randomTmpPath+ext)
            # subdomains
            randomTmpPath = self.config.get('tmpPath') + self.getRandomString()
            subDomains = github.github(domain,randomTmpPath)
            subDomains.runProccess()
            _subDomains = subDomains.getOutput()
            if _subDomains:
                for sub in _subDomains:
                    if sub not in passive:
                        passive.append(sub)
            os.remove(randomTmpPath+ext)
            # subfinder
            randomTmpPath = self.config.get('tmpPath') + self.getRandomString()
            subDomains = github.github(domain,randomTmpPath)
            subDomains.runProccess()
            _subDomains = subDomains.getOutput()
            if _subDomains:
                for sub in _subDomains:
                    if sub not in passive:
                        passive.append(sub)
            os.remove(randomTmpPath+ext)
        
        return passive

    def activeDNS(self,domains):
        from tools.dns.active import massdns 

        wordlists = self.config.get('wordlists')
        wordlists.update({'tmpPath':self.config.get('tmpPath')})
        wordlists.update({'toolPath':self.toolPath})

        active = []
        subDomains = massdns.massdns(domains,wordlists)
        subDomains.runProcess()
        _subDomains = subDomains.getOutput()
        if _subDomains:
            for sub in _subDomains:
                if sub not in active:
                    active.append(sub)
        return active
    
    def resolverProcess(self,targets):
        # resolve with massdns
        from tools.dns.resolver import massdns

        resolved = []
        wordlists = self.config.get('wordlists')
        wordlists.update({'tmpPath':self.config.get('tmpPath')})
        wordlists.update({'toolPath':self.toolPath})

        subDomain = massdns.massdns(targets,wordlists)
        subDomain.runProcess()
        _subDomains = subDomain.getOutput()
        if _subDomains:
            for sub in _subDomains:
                if sub not in resolved:
                    resolved.append(sub)
        return resolved

if __name__ == "__main__":
    castleBravoV2().startProcess()
