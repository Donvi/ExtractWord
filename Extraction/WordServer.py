#!/usr/bin/env python 2.7.8
# -*- coding: utf-8 -*-
import string
import threading,time
import sys, glob
import Queue

sys.path.append('../pylib')
sys.path.append('Mail')
sys.path.append('HbaseProxy')
sys.path.append('HdfsProxy')
sys.path.append('SE')
sys.path.append('common')
sys.path.append('DirManager')

from word import WordExtractor
from word.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import Mail2 as Mail
import HbaseProxy as Hbase_con
import getWordFromSE2 as getWordFromSE
import HdfsProxy as HdfsCon
import common
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('configure')

MAXThread = config.getint('Word Server', 'MAX Thread')
corrate = config.getfloat('Word Server', 'correct rate')

result={}
inputfil=set()
errorword={}
flock = threading.Lock()

def QB(word):
    word=word.decode("utf-8")
    restr=""
    for i in xrange(len(word)):
        c= ord(word[i])
        if c==12288:
            c=32
        elif(c >= 65281 and c <= 65374):
            c -= 65248
        restr+=unichr(c)
    return restr.encode("utf-8")

def linecount(fileName):
    count = 0
    if(not os.path.exists(fileName)): return 0
    thefile = open(fileName)
    while 1:
        buffer = thefile.read(65536)
        if not buffer: break
        count += buffer.count('\n')
    return count
    
def terminateCheck(limit,checkFile):
    linec = 0
    t=0
    tag=True
    while( limit>linec):
        time.sleep(5)      #to be finished to determine wether the all jobs done
        tlc = linecount(checkFile)
        if(linec<tlc):
            linec=tlc
            t=0
        elif(t>10):
            if(limit*corrate > linec): tag = False
            break
        else:t+=5
    return tag
    
def tryToWrite(target,limit,MailAddr,jobid):
    source=HdfsCon.FileTmp(target)
    tag=terminateCheck(limit,source)
    try:
        HdfsCon.rmRemoteFile(target)
    except Exception,e:
        Mail.send_alertMail("Exception Occured",e.message)
    try:
        print "trying to write File"
        to=MailAddr
        if(HdfsCon.writeWord(target)):
            if(tag):
                Mail.send_mail("Notification@alarm.360.cn",to,"Jobs Conmplete","Job:%s %s %s" % (jobid,u"所有词已扩展到".encode("utf-8"),target))
            else:
                Mail.send_mail("Notification@alarm.360.cn",to,u"Job Failed".encode("utf-8"),"Job:%s %s %s" % (jobid,u"部分文件失败，成功部分已经写到：".encode("utf-8"),target))
        else:
            Mail.send_mail("Notification@alarm.360.cn",to,"Jobs Failed","Job:%s %s %s" % (jobid,u"网络或者系统有异常，上传文件失败，请到临时去查找，具体请问管理员，预计存储位置".encode("utf-8"),target))
    except Exception,e:
        Mail.send_alertMail("Exception Occured",e.message)
        Mail.send_mail("Notification@alarm.360.cn",to,"Exception Occured when file is being written","Job:%s %s" % (jobid,e.message))
    if(len(errorword[target])):
        res = '\n'.join(errorword[target])
        Mail.send_mail("Notification@alarm.360.cn",to,"Job %s %s words' list in %s" % (jobid,len(errorword[target]),target),res)
    del errorword[target]
    inputfil.remove(target)
    
def normalWord(word):
    word = word.lower()
    word = QB(word)#to do more for the word map/normalize
    return word

def doWordAndWrite(word,target):
    word = doWord(word)
    try:
        HdfsCon.writeWordToTmp(word,target)
    except Exception,e:
        Mail.send_alertMail("Exception Occured",e.message)
    
def doWord(word):
    w = normalWord(word)
    extracts = ""
    extracts = getWordCached(w)
    times = 0
    while(extracts == ""):
        try:
            extracts = getWordExtracted(w)
        except Exception,e:
            errorword[target].add(word)
            print e
            break
        times += 1
        if(times>5):
            break        
    addWord(w,extracts)
    word += " " + extracts
    return word

def  getWordCached(word):
    return Hbase_con.getWord(word)

def getWordExtracted(word):
    getWord = getTryAndCheck(5,.1,getWordFromSE.get)
    return getWord(word)

def addWord(word,list):
    Hbase_con.mutate(word,list)

def sendWord(word,target):
    # constraints by the frequence of machine
    while(threading.activeCount()>MAXThread):
        time.sleep(.1)
    t=threading.Thread(target=doWordAndWrite,args=(word,target))
    t.start()

def dealWord(source,fileTarget,MailAddr):
    if(not HdfsCon.checkFile(fileTarget)):
        Mail.send_mail("",MailAddr,"File Exception Occured","The output file is not right:"+ fileTarget)
        return
    jobid = str(time.time())
    errorword[fileTarget]=set()
    try:
        wordlist = HdfsCon.getWordList(source)
    except Exception,e:
        print e
        Mail.send_mail("",MailAddr,"File Exception Occured","Can not get File "+ source)
    else:
        inputfil.remove(source)
        wordlist = wordlist.splitlines()
        inputfil.add(fileTarget)
        Mail.send_mail("",MailAddr,"Job %s Started" % jobid,"The job %s will finish in %s min(s),source:%s,target:%s" % (jobid,str(len(wordlist)*10/50000),source,fileTarget))
    try:
        HdfsCon.resetTmp(fileTarget)
    except Exception,e:
        Mail.send_alertMail(u"Exception Occured".encode("utf-8"),e.message)
    print "the main machine is OK"
    try:
        for word in wordlist:
            try:
                sendWord(word,fileTarget)
            except Exception,e:
                print word,e
        c = len(wordlist)
    except Exception,e:
        Mail.send_mail("",MailAddr,"Exception Occured","There is something wrong in the word sending system")
        Mail.send_alertMail("Exception Occured",e)
        return
    threading.Thread(target=tryToWrite,args=(fileTarget,c,MailAddr,jobid)).start()

class WordExtractorHandler:
    def __init__(self):
        self.log = {}

    def getWord(self,source,fileTarget, MailAddr):
        fileDuplicate = ""
        flock.acquire()
        if(source in inputfil):
            fileDuplicate += source + ' ' 
        if(fileTarget in inputfil):
            fileDuplicate += fileTarget + ' '
        if(fileDuplicate):
            flock.release()
            return "Threre's same file(s) running:" + fileDuplicate
        inputfil.add(source)
        flock.release()
        print 'Receiving word from:' + source
        print 'Target File at:' + fileTarget
        threading.Thread(target=dealWord,args=(source,fileTarget,MailAddr)).start()
        return 'Request Acceptted'

    def getWordList(self,word):
        print 'Extracting word' + word
        wordlist=word.split(',')
        for i in range(len(wordlist)):
            wordlist[i]=doWord(wordlist[i])
        return '\n'.join(wordlist)


handler = WordExtractorHandler()

processor = WordExtractor.Processor(handler)
transport = TSocket.TServerSocket(port = sys.argv[1])
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)

print 'Starting the server...'
server.serve()
print 'done.'
