import time

def getTryAndCheck(times,tim,func):
    def TryAndCheck(*args):
        error = None
        t = 0
        while(t<times):
            try:
                return func(*args)
            except Exception,e:
                time.sleep(tim)
                t+=1
                error = e
        raise error
    return TryAndCheck

if __name__ == '__main__':
    
    def testTry(a,b,c):
        if int(time.time()*1000) % 2:
            print a,b,c
        else: 
            raise Exception("test try")

    trial = getTryAndCheck(5,.5,testTry)
    i=0
    while(i<5):
        i+=1
        print i,":"
        trial(1,2,3)