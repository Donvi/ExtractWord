#!/usr/bin/env python
#encoding: UTF-8
import sys

sys.path.append('thrift_dir')

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from word import WordExtractor
from word.ttypes import *

transport = TSocket.TSocket('10.121.97.61', 9090)
transport = TTransport.TBufferedTransport(transport)

protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = WordExtractor.Client(protocol)
transport.open()

#contents = ColumnDescriptor(name='cf:', maxVersions=1)
#client.createTable('test', [contents])
try:
    print client.getWord(sys.argv[1],sys.argv[2],sys.argv[3])

except IOError, e:          
    print e.traceback()
    
transport.close()

