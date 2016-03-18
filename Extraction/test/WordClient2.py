import sys
import types

sys.path.append('gen-py')

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from word import WordExtractor
from word.ttypes import *

transport = TSocket.TSocket('localhost', 9090)
transport = TTransport.TBufferedTransport(transport)

protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = WordExtractor.Client(protocol)
transport.open()

#contents = ColumnDescriptor(name='cf:', maxVersions=1)
#client.createTable('test', [contents])
try:
    client.getWord(r"/home/hdp-guanggao-intern/user/tangweihan/t.d",r"/home/hdp-guanggao-intern/user/tangweihan/4.data")

except IOError, e:          
    print e.traceback()
    
transport.close()

