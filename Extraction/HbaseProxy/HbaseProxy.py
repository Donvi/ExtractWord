import sys,threading
import Queue
import traceback

import DirManager

thrift_dir = DirManager.getThriftPath()
sys.path.append(thrift_dir)
sys.path.append(DirManager.getHomeDir(__file__))

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from hbase import Hbase
from hbase.ttypes import *

import ConfigParser
config = ConfigParser.RawConfigParser()
config.read(DirManager.getConfigPath())
update_len = config.getint('Hbase', 'update time length')
hbaseAddr = config.get('Hbase', 'hbase address')
hbasePort = config.getint('Hbase', 'hbase port')
tableName = config.get('Hbase', 'table name')

reader={}
writer=[]

def newConn():
    try:
        transport = TSocket.TSocket(hbaseAddr, hbasePort)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = Hbase.Client(protocol)
        transport.open()
        return client
    except Exception,e:
        print e
        return None

qlock = threading.Lock()
connQueue = Queue.Queue(100)

def getClient():
    qlock.acquire()
    if(connQueue.empty()):
        qlock.release()
        client = newConn()
        return client
    else:
        client = connQueue.get()
        qlock.release()
        client._iprot.trans.open()
        return client

def giveBackCli(client):
    if(client):
        client._iprot.trans.close()
        connQueue.put_nowait(client)

def detectAndOpenCon(transport):
    while(not transport.isOpen()):transport.open()

def getWord(word):
    client = getClient()
    if(not client):return ""
    results = ""

    try:
        results=client.getRow(tableName,word,{})
    except IOError, e:          
        print ('Check env failed, error code (%s)' % str(e.returncode))
    except Exception, e:
        print traceback.print_exc()

    giveBackCli(client)
    if(len(results)==0): return ""
    else: return results[0].columns["word:v"].value

def mutate(row,content):
    client = getClient()
    if(not client):return ""
    try:
        wordlist1 = Mutation(column='word:v',value=str(content))
        wordlist2 = Mutation(column='word:time',value=str(update_len))
        client.mutateRow(tableName,str(row),[wordlist1,wordlist2],{})
    except IOError, e:          
        print ('Check env failed, error code (%s)' % str(e.returncode))
    except Exception, e:
        print traceback.print_exc()
    finally:
        giveBackCli(client)
    

def mutateRow(row,columns,values):
    client = getClient()
    try:
        wordlist1 = Mutation(column=columns,value=values)
        client.mutateRow(tableName,row,[wordlist1],{})
    except IOError, e:          
        print ('Check env failed, error code (%s)' % str(e.returncode))
    except Exception, e:
        print e
    finally:
        giveBackCli(client)

def getWords(constrainWords):
    client = getClient()
    scanner = client.scannerOpen(tableName,constrainWords,[],{})
    r = client.scannerGet(scanner)
    result= []
    while r:
        print r[0]
        result.append(r[0])
        r = client.scannerGet(scanner)
    giveBackCli(client)
    return result

if (__name__ =='__main__'):
    print getWord('flower')
