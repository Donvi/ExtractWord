# -*- coding: utf-8 -*-
import sys
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.utils import COMMASPACE,formatdate
from email.mime.text import MIMEText

server={}
server['name']="mail.alarm.360.cn"
server['user']='tangweihan@alarm.360.cn'
server['passwd']='twhddt1990,,,,,' 

def send_mail(fro, to, subject, text, files=[]): 
    assert type(server) == dict 
    assert type(to) == list 
    assert type(files) == list 
 
    msg = MIMEMultipart() 
    msg['From'] = fro
    msg['Subject'] = subject 
    msg['To'] = COMMASPACE.join(to) #COMMASPACE==', ' 
    msg['Date'] = formatdate(localtime=True) 
    msg.attach(MIMEText(text)) 
 
    for file in files: 
        part = MIMEBase('application', 'octet-stream') #'octet-stream': binary data 
        part.set_payload(open(file, 'rb'.read())) 
        encoders.encode_base64(part) 
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file)) 
        msg.attach(part) 
 
    smtp = smtplib.SMTP(server['name']) 
    print smtp.login(server['user'], server['passwd'])
    print smtp.verify("tangweihan@alarm.360.cn")
    smtp.sendmail(fro, to, msg.as_string()) 
    smtp.close()

if __name__ == '__main__':
    to=["tangweihan@360.cn",]
    send_mail("tangweihan@alarm.360.cn",to,u"任务完成".encode("utf-8"),"All word has been extracted")
