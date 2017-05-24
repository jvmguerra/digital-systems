#!/usr/bin/env python
 
import sys
sys.path.append('../gen-py')
 
from graphdb import GraphCRUD
from graphdb.ttypes import *
 
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
 
import socket
from threading import Lock
import time

global lock
lock = Lock()

class GraphHandler:

  def __init__(self):
    self.log = {}
    self.vertexList = []
    self.edgeList = []
    self.listOfVertex = []
    self.adjacentVertex =[]

  def readFile(self):

    lock.acquire()
    with open("../vertex-list", "r") as file:
        self.vertexList = []
        for line in file:
            line = line.replace("\n","")
            args = line.split(",")
            if args[0] != '':
              vertex = Vertex(int(args[0]), int(args[1]), int(args[2]))
              self.vertexList.append(vertex)

    with(open("../edge-list","r")) as file:
        self.edgeList = []
        for line in file:
            line = line.replace("\n","")
            args = line.split(",")
            v1 = self.searchVertex(int(args[0]))
            v2 = self.searchVertex(int(args[1]))
            if(v1 != None and v2 != None):
                edge = Edge(v1, v2, int(args[2]), int(args[3]))
                self.edgeList.append(edge)

    lock.release()
    return Graph(self.vertexList, self.edgeList)

  def searchVertex(self, id):
    for v in self.vertexList:
      if v.id == id:
        return v
    return None

  def searchEdge(self, v1, v2):
    for e in self.edgeList:
      if((e.v1 == v1 and e.v2 == v2) or (e.v2 == v1 and e.v1 == v2)):
          return e
    return None

  def insertNewVertex(self, vertex):
    lock.acquire()
    with open("../vertex-list","a") as f:
        f.write(str(vertex.id) + ',' + str(vertex.color) + ',' + str(vertex.weight) + '\n')
        time.sleep(60)
    lock.release()

  def insertNewEdge(self, edge):
    lock.acquire()
    with open("../edge-list", "a") as f:
        f.write(str(edge.v1) + ',' + str(edge.v2) + ',' + str(edge.weight) + ',' + str(edge.direction) + '\n')
    lock.release()

  def createVertex(self, vertex):
    self.readFile()
    if (self.searchVertex(vertex.id) ==  None):
      self.insertNewVertex(vertex)
      print('Vertice Inserido')
    else:
      print('Vertice ja existe')

  def createEdge(self, v1, v2, weight, direction):
    self.readFile()
    if (self.searchEdge(v1,v2) == None and v1 != v2):
      self.insertNewEdge(Edge(v1,v2,weight,direction))
      print('Vertice Inserido')
    elif v1 == v2:
      print('Vertices iguais!')
    else:
      print('Vertice ja existente')

  def updateVertex(self, vertex):
    self.vertexList = []
    self.readFile()
    if (self.searchVertex(vertex.id) != None):
      for v in self.vertexList:
        if v.id == vertex.id:
          v.color = vertex.color
          v.weight = vertex.weight

      lock.acquire()
      with open("../vertex-list", "w") as f:
        f.write(self.vertexListToString())
      lock.release()
      print('Vertice atualizado')
    else:
      print('Vertice nao existente')

  def updateEdge(self, v1, v2, weight, direction):
    self.edgeList = []
    self.readFile()
    for e in self.edgeList:
      if ((e.v1 == v1 and e.v2 == v2) or (e.v1 == v2 and e.v2 == v1) and v1!=v2):
        e.weight = weight
        e.direction = direction
      
    lock.acquire()
    with open("../edge-list", "w") as f:
      f.write(self.edgeListToString())
    lock.release()
    print('Aresta atualizado')

  def readVertex(self, v1):
    self.readFile()
    vertex = self.searchVertex(v1)
    if vertex != None:
      return vertex
    else:
      e = ElementNotFoundException()
      raise(e)

  def readEdge(self, v1, v2):
    self.readFile()
    edge = self.searchEdge(v1,v2)
    if edge != None:
      return edge
    else:
      e = ElementNotFoundException()
      raise (e)

  def deleteVertex(self, vertex):
    self.vertexList = []
    self.edgeList = []
    self.readFile()
    if (self.searchVertex(vertex) != None):
      for v in self.vertexList:
        if v.id == vertex:
          self.vertexList.remove(v)

      for e in self.edgeList[:]:
        if e.v1.id == vertex or e.v2.id == vertex:
          self.edgeList.remove(e)
            
      lock.acquire()
      with open("../vertex-list", "w") as f:
        f.write(self.vertexListToString())
      with open("../edge-list", "w") as f:
        f.write(self.edgeListToString())
      lock.release()
      print('Vertice excluido')
    else:
      print('Vertice nao encontrado')

  def deleteEdge(self, v1, v2):
    self.edgeList = []
    self.readFile()
    for e in self.edgeList:
      if(v1 != v2 and ((e.v1.id == v1 and e.v2.id == v2) or (e.v1.id == v2 and e.v2.id == v1))):
        self.edgeList.remove(e)
    lock.acquire()
    with open("../vertex-list", "w") as f:
      f.write(self.vertexListToString())
    with open("../edge-list", "w") as f:
      f.write(self.edgeListToString())
    lock.release()

  def vertexListToString(self):
    string = ''
    for v in self.vertexList:
      subs = str(v.id) + ',' + str(v.color) + ',' + str(v.weight) + '\n'
      string = string + subs
    return string

  def edgeListToString(self):
    string = ''
    for e in self.edgeList:
      subs = str(e.v1.id) + ',' + str(e.v2.id) + ',' + str(e.weight) + ',' + str(e.direction) + '\n'
      string = string + subs
    return string

  def listVertexEdges(self, vertex):
    self.listOfVertex = []
    self.readFile()

    if self.searchVertex(vertex) != None:
      for e in self.edgeList:
        if( e.v1.id == vertex or e.v2.id == vertex):
          self.listOfVertex.append(e)
      return self.listOfVertex
    else:
      e = ElementNotFoundException()
      raise (e)


  def listAdjacentVertex(self, vertex):
    self.adjacentVertex = []
    self.readFile()

    if self.searchVertex(vertex) != None:
      for e in self.edgeList:
        if e.v1.id == vertex:
          self.adjacentVertex.append(e.v2)
        elif e.v2.id == vertex:
          self.adjacentVertex.append(e.v1)
      print(self.adjacentVertex)
      return self.adjacentVertex
    else:
      e = ElementNotFoundException()
      raise (e)
    

handler = GraphHandler()
processor = GraphCRUD.Processor(handler = handler)
transport = TSocket.TServerSocket(host='localhost', port='9090')
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()
 
server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
 
print ("Starting python server...")
server.serve()
print ("done!")