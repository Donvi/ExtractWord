import sys
import os,hashlib,threading

import DirManager

sys.path.append(DirManager.getPylibPath())
sys.path.append(DirManager.getFileDir("Mail"))

import paramiko,base64
import Mail2 as Mail

import ConfigParser
config = ConfigParser.RawConfigParser()
config.read(DirManager.getConfigPath())
clientName = config.get('HDFS', 'client name')
username = base64.decodestring(config.get('HDFS', 'user name'))
password = base64.decodestring(config.get('HDFS', 'password'))
hdpuser = config.get('HDFS', 'hadoop user name')
hdppath = config.get('HDFS', 'hadoop path')
hdptmppath = config.get('HDFS', 'hadoop get path')
hdpputpath = config.get('HDFS', 'hadoop put path')

lock=threading.Lock()

def linecount(fileName):
    count = 0
    if(not os.path.exists(fileName)): return 0
    thefile = open(fileName)
    while 1:
        buffer = thefile.read(65536)
        if not buffer: break
        count += buffer.count('\n')
    return count

def executeCmd(command):
    print "ssh2 execute command: %s" %(command)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(clientName, username = username, password = password)
    stdin, stdout, stderr = ssh.exec_command(command)
    print "finish: %s" %(command)
    stdin.write(password+"\n")
    stdin.flush()
    tmp=stderr.read()
    if(tmp):
        print tmp
        Mail.send_alertMail("Exception Occured",command+"\n Error:"+tmp)
        if(tmp.find("Password") == -1):raise Exception(tmp)
    result = stdout.read()
    stdin.close()
    stdout.close()
    stderr.close()
    ssh.close()
    print "finish ssh connecting"
    return result

def FileMap(addr):
    return hashlib.md5(addr).hexdigest()

def FileTmp(addr):
    return os.path.join("temp",FileMap(addr))

def getWordList(source):
    tmpsource = hdptmppath+FileMap(source)
    try:
        rmFile(tmpsource)
    except Exception,e:
        print e
    command = "sudo -H -u %s %s fs -get %s %s" % (hdpuser,hdppath,source,tmpsource)
    executeCmd(command)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(clientName, username = username, password = password)
    sftp = ssh.open_sftp()
    tmp = FileTmp(source)
    print "local:"+tmp
    print "remote temp:"+tmpsource
    if(not os.path.exists(os.path.dirname(tmp))):
        os.makedirs(os.path.dirname(tmp))
    try:
        sftp.get(tmpsource,tmp)
    except Exception,e:
        print e.traceback()
    finally:    
        sftp.close()
        ssh.close()
        rmFile(tmpsource)
    f = open(tmp)
    result = f.read()
    f.close()
    os.remove(tmp)
    return result

def resetTmp(target):
    if(os.path.isfile(FileTmp(target))):
        os.remove(FileTmp(target))

def writeWordToTmp(word,target):
    lock.acquire()
    f=open(FileTmp(target),"a")
    print >>f,word
    f.close()
    lock.release()

def writeWord(target):
    tmp = FileTmp(target)
    if(not os.path.exists(tmp)):return False
    source = '/'.join((hdpputpath, FileMap(target)))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(clientName, username = username, password = password)
    sftp = ssh.open_sftp()
    print "local:"+tmp
    print "remote temp:"+source
    sftp.put(tmp,source)
    sftp.close()
    ssh.close()
    os.remove(tmp)

    try:
        command = "sudo -H -u %s %s fs -put %s %s"%(hdpuser,hdppath,source,target)
        executeCmd(command)
    except Exception,e:
        print e
        print "there's error in command execution"
        return False
    finally:
        command = "rm -f %s"%(source)
        executeCmd(command)
    return True

def checkFile(testFile):
    command = 'touch %s' % (os.path.join(hdpputpath,FileMap(testFile)))
    try:
        executeCmd(command)
    except Exception,e:
        print e
        return False
    else:
        return True
def getFileLines(file):
    command = 'sudo -H -u %s cat %s|grep -c ""'%(hdpuser,file)
    return int(executeCmd(command))

def rmFile(file):
    command = "sudo -H -u %s rm -f %s" % (hdpuser,file)
    return executeCmd(command)

def rmRemoteFile(file):
    command = "sudo -H -u %s %s fs -rm %s" % (hdpuser,hdppath,file)
    return executeCmd(command)

if __name__ == '__main__':
    print writeWord('/home/hdp-ads-audit/user/yangjun/search_expand/for-weihan/test.out')

