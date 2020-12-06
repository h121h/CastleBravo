# CastleBravo V2 - BugBounty Automation
# by @m4ll0k - github.com/m4ll0k

def readfile(_path):
    if _path:
        k = []
        with open(_path,'r') as file_:
            for line in file_:
                line = line.strip()
                k.append(line)
        return k 
    return  