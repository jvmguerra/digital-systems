import multiprocessing
import socket
import os
import sys
import threading
import configparser

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
            command = raw_input('Qual comando deseja realizar? (C,R,U,D)')
            mapItem = raw_input('Item que deseja realizar a operacao: ')
        except EOFError:
            return
        UDPClientSocket.sendto(str.encode(command+mapItem), serverAddressPort)

def receiveCommand():
    while True:
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)

config              = configparser.ConfigParser()
config.read('./settings.ini')
serverAddressPort   = (str(config.get('SERVER', 'host')), int(config.get('SERVER', 'port')))
bufferSize          = int(config.get('SERVER', 'packetBytes'))
UDPClientSocket     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
jobs                = []

def main():
    newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
    initializeThreads(newstdin)

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()

if __name__ == '__main__':
    main()