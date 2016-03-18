import os
homepath = os.path.dirname(__file__)

def getPylibPath():
    return os.path.join(homepath,'..','..','pylib')
    
def getThriftPath():
    return os.path.join(homepath,'..','thrift_dir')
    
def getConfigPath():
    return os.path.join(homepath,'..','configure')
    
def getFileDir(name):
    return os.path.join(homepath,'..',name)
    
def getHomeDir(fileAddr):
    return os.path.dirname(fileAddr)