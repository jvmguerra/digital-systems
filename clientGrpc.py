from __future__ import print_function

import grpc

import crud_pb2
import crud_pb2_grpc

import multiprocessing
import socket
import os
import sys
import threading
import configparser
import json
import time

def initializeThreads(newstdin):
    initializeCommandThread(newstdin)
    initializeDisplayThread()

def initializeCommandThread(newstdin):
    process = multiprocessing.Process(target = sendCommand, args = (newstdin, ))
    jobs.append(process)

def initializeDisplayThread():
    process = multiprocessing.Process(target = receiveCommand, args = ())
    jobs.append(process)

def sendCommand(newstdin):
    sys.stdin = newstdin
    while True:
        try:
            message = ''
            time.sleep(.1)
            command = input('Qual comando deseja realizar? (1: C, 2: R, 3: U, 4: D): ')
            mapItem = input('Item que deseja realizar a operacao: ')
            if int(command) != 4:
                monitoring = input('Deseja monitorar o item? (0: N, 1: S): ')
            if validator(command, mapItem):
                if (int(command) == 1 or int(command) == 3):
                    message = str(input('String: '))
                jsonItem = {
                    'command': command,
                    'item': mapItem,
                    'string': message,
                    'ip': ipAddress,
                    'port': clientAddress[1],
                    'monitoring': monitoring
                }
                response = stub.SendCommand(crud_pb2.ItemRequest(
                    command=jsonItem['command'],
                    item=jsonItem['item'],
                    message=jsonItem['string'],
                    ip=jsonItem['ip'],
                    port=jsonItem['port'],
                    monitoring=int(jsonItem['monitoring']))
                )
            else:
                print('Dados Invalidos')
        except EOFError:
            return

def validator(command, mapItem):
    try:
        if (int(command) >= 1 and int(command) <=4 and int(mapItem)):
            return True
    except:
        return False

def receiveCommand():
    UDPClientSocket.bind(clientAddress)
    while True:
        msgFromServer, addr = UDPClientSocket.recvfrom(bufferSize)
        msg = "\nMessage from Server: "
        print(msg + str(msgFromServer.decode()))

config              = configparser.ConfigParser()
config.read('./settings.ini')
serverAddressPort   = (str(config.get('SERVER', 'host')), int(config.get('SERVER', 'port')))
bufferSize          = int(config.get('SERVER', 'packetBytes'))

port = input('Digite uma porta para o cliente: ')

UDPClientSocket     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ipAddress = socket.gethostbyname(socket.gethostname())
clientAddress = (ipAddress, int(port))

jobs                = []

channel = grpc.insecure_channel(serverAddressPort[0] + ':' + str(serverAddressPort[1]))
stub = crud_pb2_grpc.CrudGrpcStub(channel)

def main():
    newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
    initializeThreads(newstdin)

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()

if __name__ == '__main__':
    main()