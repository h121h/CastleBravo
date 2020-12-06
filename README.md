### CastleBravo
CastleBravo - BugBounty Automation Tool 

This repo. contains only some parts of the full version , if you want the most complete version contact me here m4ll0k@protonmail.com or via [twitter](https://twitter.com/m4ll0k)


### requirements

- active dns 
  - `massdns`
  - `altdns`
  
- passive dns
  - `crobat`
  - `amass`
  - `assetfinder`
  - `github-subdomains`
  - `subfinder`
  - `subdomain.sh`
 

- your [telegram bot ](https://core.telegram.org/bots)
  - `token and chatid`
  
  
 
 ### installation 
 
 - download castlebravo 
 
 `git clone https://github.com/m4ll0k/CastleBravo.git`
 
 - download `massdns`
 - download and compile all tools in `passive dns` and then move them to the `CastleBravo/tools/dns/passive/tools/` folder
   - [crobat](https://sonar.omnisint.io/) 
   - [amass](https://github.com/OWASP/Amass) - put your `config.ini` in `CastleBravo/tools/dns/passive/tools/`
   - [assetfinder](https://github.com/tomnomnom/assetfinder) 
   - [subfinder](https://github.com/projectdiscovery/subfinder) - put your `config.yaml` in `CastleBravo/tools/dns/passive/tools/`
   - [github-subdomains](https://github.com/gwen001/github-search/blob/master/github-subdomains.py) put `.tokens` in `CastleBravo/tools/dns/passive/tools/`
 
 
 
 
### setup

- edit `config.json`

```json

{
    "inScope"     : ["example.com"],
    "outScope"    : ["dev.example.com"],
    "target"      : "example.com",
    "projectName" : "exampleTarget",
    "keys" : {
        "telegramToken":"[YOUR_TELEGRAM_BOT_TOKEN]",
        "chatId":"[TELEGRAM_CHATID]"
    },
    "dbPath"   : "/db/",
    "toolName" : "CastleBravoV2",
    "tmpPath" : "/tmp/",
    "dbExt" : ".db",
    "wordlists":{
        "altdnsSmall" : "/wordlist/dns/small.txt",
        "altdnsMedium" : "/wordlist/dns/medium.txt",
        "altdnsBig" : "/wordlist/dns/big.txt",
        "massdnsResolvers" : "/wordlist/dns/resolvers.txt"
    }
}

```

- now run it, with crontab,etc (`I suggest you to use the tool in your VPS`) or or directly with python:

```bash

$ python3 castlebravo.py

```



