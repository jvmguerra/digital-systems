import multiprocessing
import socket
import os
import configparser

config = configparser.ConfigParser()
config.read('./settings.ini')

def initializeThreads():
    initializeCommandThread()
    # initializeDisplayThread()

def sendCommand():
    while True:
        try:
            msg = raw_input('Type')
        except EOFError:
            return
        s.sendto(msg, server_address)

def receiveCommand():
    while True:
        print s.recvfrom(1400)

def initializeCommandThread():
    process = multiprocessing.Process(target = sendCommand, args = ())
    jobs.append(process)

def initializeDisplayThread():
    process = multiprocessing.Process(target = receiveCommand, args = ())
    jobs.append(process)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = config.get('CLIENT', 'host')
port = config.get('CLIENT', 'port')

server_address = (host, port)

# s.connect((str(host), int(port)))
jobs = []
initializeThreads()

for j in jobs:
    j.start()

for j in jobs:
    j.join()
s.close()