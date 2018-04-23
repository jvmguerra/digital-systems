class Pile(object):
    def __init__(self):
        self.queue = []

    def insert(self, element):
        self.queue.append(element)

    def read(self):
        return self.queue

    def remove(self):
        return self.queue.pop(0)

    def empty(self):
        return len(self.queue) == 0