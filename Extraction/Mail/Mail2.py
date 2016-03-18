# -*- coding: utf-8 -*-
import os,threading,sys
import DirManager
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read(DirManager.getConfigPath())
alertMail =  config.get('MAIL', 'alert mail')

lock = threading.Lock()

def send_mail(fro, to, subject, text, files=[]): 
    lock.acquire()
    text = str(text)
    try:
        if(text):
            text = text.replace('\n','<br/>').replace(' ','&nbsp;')
            f=open("MailBody","w")
            print >>f,text
            f.close()
        print 'mail "%s" to %s' % (subject,to)
        os.system('bash %s/mail.sh "%s" %s' % (DirManager.getFileDir("Mail"),subject,to))
    except Exception,e:
        print e
    finally:
        lock.release()

def send_alertMail(subject, text):
    send_mail("",alertMail,subject,text)

if __name__ == '__main__':
    send_mail("","tangweihan@360.cn","test","a\n b\n c\n d")
