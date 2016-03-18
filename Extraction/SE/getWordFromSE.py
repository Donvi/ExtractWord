import pycurl
import urllib
import StringIO
import json
import time
import threading
# -*- coding: utf-8 -*-

fromlist=("kvdb","engine")
timelist=[0 for i in xrange(200)]
lock = threading.Lock()
log=open("selog.log","w")

def get(word):
    try:
        word = urllib.quote(word)
    except Exception,e:
        print e
        print >>log,word
    httpReq = "http://10.138.240.122:9501/mod_searcher/Search?a=223.15.209.0&f=1&s=0&c=30&q="+word
    print httpReq
    lock.acquire()
    t=time.time()
    while(t-timelist[0]<1): 
        time.sleep(.1)
        t=time.time()
    timelist.append(t)
    del timelist[0]
    lock.release()
    curl = pycurl.Curl()
    curl.setopt( pycurl.FOLLOWLOCATION, 1L )
    curl.setopt( pycurl.NOSIGNAL, 1L )
    b = StringIO.StringIO()
    curl.setopt( pycurl.WRITEFUNCTION, b.write)
    curl.setopt( pycurl.WRITEDATA, b )
    curl.setopt( pycurl.URL, httpReq )
    try:
        curl.perform()
    except Exception,e:
        print e
        print >>log,word
    curl.close()
    content=b.getvalue()
    content = unicode(content,"utf-8").encode("utf-8")
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
            title = title.replace("<b>","").replace("</b>","")
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
    return json.dumps(result,ensure_ascii=False)
def close():
    log.close()

if __name__ == '__main__':
    print get("old scroll")
