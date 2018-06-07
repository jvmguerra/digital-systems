from concurrent import futures
import time
import grpc
import crud_pb2
import crud_pb2_grpc

import multiprocessing
from multiprocessing.managers import BaseManager
import socket
import os
import sys
import threading
import configparser
import json
from classes.pile import Pile
from classes.structure import Structure
from classes.crudGrpc import CrudGrpc
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class MyManager(BaseManager):
    pass

MyManager.register('Pile', Pile)
MyManager.register('Structure', Structure)

def initializeThreads(newstdin, commandsPile, persistencePile, responsePile, memory):
    initReceiverThread(serverAddressPort, commandsPile)
    initReceiverGrpcThread(serverAddressPort, commandsPile)
    initRecipientThread(commandsPile, persistencePile, responsePile, memory)
    initPersistenceThread(persistencePile, memory)
    initResponseThread(responsePile)
    initLogThread(memory)

def initLogThread(memory):
    process = multiprocessing.Process(target = loggerThread, args = (memory, ))
    jobs.append(process)

def initReceiverThread(serverAddressPort, commandsPile):
    process = multiprocessing.Process(target = receiverThread, args = (serverAddressPort, commandsPile))
    jobs.append(process)

def initReceiverGrpcThread(serverAddressPort, commandsPile):
    process = multiprocessing.Process(target = receiverGrpcThread, args = (serverAddressPort, commandsPile))
    jobs.append(process)

def initRecipientThread(commandsPile, persistencePile, responsePile, memory):
    process = multiprocessing.Process(target = recipientThread, args = (commandsPile, persistencePile, responsePile, memory))
    jobs.append(process)

def initPersistenceThread(persistencePile, memory):
    process = multiprocessing.Process(target = persistenceThread, args = (persistencePile, memory))
    jobs.append(process)

def initResponseThread(responsePile):
    process = multiprocessing.Process(target = responseThread, args = (responsePile, ))
    jobs.append(process)

def receiverGrpcThread(serverAddressPort, commandsPile):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    crud_pb2_grpc.add_CrudGrpcServicer_to_server(CrudGrpc(commandsPile), server)
    server.add_insecure_port(serverAddressPort[0] + ':' + str(serverAddressPort[1]))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

def loggerThread(memory):
    while True:
        if not memory.logListIsEmpty():
            memory.saveLogListAnLogFile()

def persistLogs():
    print('Every 120 seconds')

def receiverThread(serverAddressPort, commandsPile):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(serverAddressPort)
    while True:
        (data, addr) = s.recvfrom(bufferSize)
        clientData = {
            'client': addr,
            'data': json.loads(data.decode())
        }
        commandsPile.insert(clientData)

def recipientThread(commandsPile, persistencePile, responsePile, memory):
    sched.add_job(persistLogs, 'interval', seconds = 120)
    sched.start()
    while True:
        if not commandsPile.empty():
            message = 'Sucesso'

            # execute task
            task = commandsPile.remove()
            command = int(task['data']['command'])
            item = task['data']['item']
            string = task['data']['string']
            monitoring = task['data']['monitoring']

            if(command == 1):
                memory.createItem({item: string})
            elif(command == 2):
                itemFound = memory.readItem(item)
                message = 'Item não encontrado' if not itemFound else itemFound
            elif(command == 3):
                message = 'Atualizado com sucesso' if memory.updateItem({item: string}) else 'Item não encontrado'
            elif(command == 4):
                message = 'Deletado com sucesso' if memory.deleteItem(item) else 'Falha ao deletar'
            elif(command == 5):
                if monitoring == 1:
                    memory.addMonitoring(item, task['client'])

            sendNotice(item, memory)
                
            # send command to persistencePile
            # persistencePile.insert(memory.readAll())

            memory.addCommandAnLogList({'command': command, 'item': item, 'data': string, 'client': task['client'], 'monitoring': monitoring})

            # send message y/n to responsePile
            responsePile.insert({
                'message': message,
                'client': task['client']
            })

def sendNotice(item, memory):
    customers = memory.getCustomersMonitors(item)
    if len(customers) != 0:
        for customer in customers:
            message = 'Chave ' + str(item) + ' foi consultada ou modificada!'
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(message.encode(), customer)

def persistenceThread(persistencePile, memory):
    while True:
        if not persistencePile.empty():
            task = persistencePile.remove()
            memory.saveItems(task)

def responseThread(responsePile):
    while True:
        if not responsePile.empty():
            task = responsePile.remove()
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(task['message'].encode(), (str(task['client'][0]), int(task['client'][1])))

def excuteLogCommands(memory):
    commandsList = memory.getLogListToExecute()

    for command in commandsList:
        commandToExecute = command['command']
        item = command['item']
        data = command['data']
        monitoring = command['monitoring']
        client = command['client']
        
        if(commandToExecute == 1):
            print('Criando novo item: chave ' + item)
            memory.createItem({item: data})
        elif(commandToExecute == 3):
            if memory.updateItem({item: data}):
                print('Item atualizado: chave ' + item)
            else:
                print('Item não encontrado')
        elif(commandToExecute == 4):
            if memory.deleteItem(item):
                print('Item deletado: chave ' + item)
            else:
                print('Falha ao deletar')
        elif(commandToExecute == 5):
            if monitoring == 1:
                memory.addMonitoring(item, (client[0], client[1]))

config = configparser.ConfigParser()
config.read('./settings.ini')

serverAddressPort   = (str(config.get('SERVER', 'host')), int(config.get('SERVER', 'port')))
bufferSize          = int(config.get('SERVER', 'packetBytes'))
jobs                = []

def main():

    # Managers - Custom classes accessed by multiple processes
    manager = MyManager()
    manager.start()
    commandsPile = manager.Pile()
    persistencePile = manager.Pile()
    responsePile = manager.Pile()

    # Shared memory
    memory = manager.Structure()
    memory.loadItems()
    memory.loadItensOfLogFile()
    excuteLogCommands(memory)

    # Initializes all of the servers 4 'threads'
    newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
    initializeThreads(newstdin, commandsPile, persistencePile, responsePile, memory)

    for job in jobs:
        job.start()

    for job in jobs:
        job.join()

if __name__ == '__main__':
    main()