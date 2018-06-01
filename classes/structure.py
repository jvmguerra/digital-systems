import json

class Structure(object):
    def __init__(self):
        self.dict = dict()
        self.monitoringDict = dict()
        self.logList = []
        self.logsToRun = []

    def readAll(self):
        return self.dict

    def loadItems(self):
        with open('data.json', 'r') as json_data:
            self.dict = json.load(json_data)

    def saveItems(self, itens):
        jsonTest = json.dumps(itens)
        file = open('data.json', 'w')
        file.write(jsonTest)
        file.close()

    def createItem(self, mapItem):
        self.dict.update(mapItem)

    def readItem(self, mapItem):
        if self.dict.get(mapItem) is None:
            return False
        return self.dict[mapItem]

    def updateItem(self, mapItem):
        if self.dict.get(list(mapItem)[0]) is None:
            return False
        else:
            self.dict.update(mapItem)
            return True

    def deleteItem(self, mapItem):
        try:
            del self.dict[mapItem]
            return True
        except:
            return False

    def addMonitoring(self, item, client):
        if item in self.monitoringDict:
            if not self.onMonitoringAlreadyExists(item, client):
                self.monitoringDict[item].append(client)
                print(self.monitoringDict)
            else:
                print('Chave ja monitorada!')
        else:
            self.monitoringDict[item] = [client]
            print(self.monitoringDict)

    def onMonitoringAlreadyExists(self, item, client):
        exist = False
        for elemClient in self.monitoringDict[item]:
            if elemClient[1] == client[1]:
                exist = True
        return exist

    def getCustomersMonitors(self, item):
        customers = []
        if item in self.monitoringDict:
            customers = self.monitoringDict[item]
        return customers

    def deleteCustomersMonitors(self, item):
        if item in self.monitoringDict:
            del self.monitoringDict[item]

    def logListIsEmpty(self):
        return len(self.logList) == 0

    def addCommandAnLogList(self, objMethod):
        # print(objMethod)
        self.logList.append(objMethod)

    def saveLogListAnLogFile(self):
        file = open('log.txt', 'a')
        for itemLog in self.logList:
            file.write('%s\n' % json.dumps(itemLog))
            file.close()
        self.logList = []

    def loadItensOfLogFile(self):
        file = open('log.txt', 'r')
        for item in file:
            self.logsToRun.append(eval(item))
        # print(self.logsToRun)

    def getLogListToExecute(self):
        return self.logsToRun