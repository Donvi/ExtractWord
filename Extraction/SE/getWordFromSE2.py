import urllib2
import StringIO
import json
import time
import threading,sys
# -*- coding: utf-8 -*-

import DirManager
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read(DirManager.getConfigPath())
seAddress = config.get('Search Engine', 'search engine address')
fromlist = config.get('Search Engine', 'available source').split(',')

timelist = [0 for i in xrange(200)]
lock = threading.Lock()

def get(word):
    log = open ("selog.log","a")
    try:
        word = urllib2.quote(word)
    except Exception,e:
        print >>log,word
        raise Exception("Word Error")
    httpReq = seAddress+word
    #print httpReq
    lock.acquire()
    t=time.time()
    while(t-timelist[0]<1): 
        time.sleep(.1)
        t=time.time()
    timelist.append(t)
    del timelist[0]
    lock.release()
    content=urllib2.urlopen(httpReq)
    content = unicode(content.read(),"utf-8").encode("utf-8")
    result={}
    result[word]=[]
    url_key = 's:3:"url";'
    title_key = 's:5:"title";'
    summmary_key = 's:7:"summary";'
    from_key = 's:4:"from";'
    rank=0
    pos = content.find(from_key)
    pos_o = pos
    while(pos!=-1):
        pos = content.find('"',pos+len(from_key))
        fro = content[pos+1:content.find('"',pos+1)]
        pos = content.rfind(url_key,0,pos)
        pos = content.find('"',pos+len(url_key))
        url = content[pos+1:content.find('"',pos+1)]
        if(fro in fromlist):
            rank+=1
            pos = content.find(title_key,pos)
            pos = content.find('"',pos+len(title_key))
            title = content[pos+1:content.find('"',pos+1)]
            pos = content.find(summmary_key,pos)
            pos = content.find('"',pos+len(summmary_key))
            summary = content[pos+1:content.find('"',pos+1)]
            title = title.replace(r"<b>","").replace(r"</b>","")
            summary = summary.replace("<b>","").replace("</b>","")
            result[word].append({
                "url":url,
                "title":title,
                "summary":summary,
                "rank":str(rank)
                })
        if(pos<pos_o):
            pos = content.find(from_key,pos_o+1)
        pos_o=pos
    log.close()
    return json.dumps(result,ensure_ascii=False)

if __name__ == '__main__':
    print get("old scroll")
