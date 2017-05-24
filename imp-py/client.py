#!/usr/bin/env python
 
import sys
sys.path.append('../gen-py')
 
from graphdb import GraphCRUD
from graphdb.ttypes import *
 
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
 
try:
  # Make socket
  transport = TSocket.TSocket('localhost', 9090)
 
  # Buffering is critical. Raw sockets are very slow
  transport = TTransport.TBufferedTransport(transport)
 
  # Wrap in a protocol
  protocol = TBinaryProtocol.TBinaryProtocol(transport)
 
  # Create a client to use the protocol encoder
  client = GraphCRUD.Client(protocol)
 
  # Connect!
  transport.open()
 
  # # vertex CRUD
  # client.createVertex(Vertex(5,1,1))
  print(client.readVertex(5))
  # client.updateVertex(Vertex(1,4,4)),
  # client.deleteVertex(1),

  # # edges CRUD
  # client.createEdge(1,2,1,0)
  # client.readEdge(1,2)
  # client.updateEdge(1,2,2,0)
  # client.deleteEdge(1,2)

  # # list vertex edges
  # print(client.listVertexEdges(1))

  # # list vertex neighbors
  # print(client.listAdjacentVertex(1))
 
  transport.close()
 
except Thrift.TException, tx:
  print ("%s" % (tx.message))