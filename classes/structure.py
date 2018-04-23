import json

class Structure(object):
    def __init__(self):
        self.dict = dict()

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