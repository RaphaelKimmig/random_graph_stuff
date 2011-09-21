from heapq import heappush, heappop, heapify
from itertools import repeat

def constant_factory(value):
    return repeat(value).next

class PriorityQueue(object):
    def __init__(self):
        self.pq = []
        self.elements = {}

    def is_empty(self):
        return not self.pq

    def insert(self, element, key):
        heappush(self.pq, (key, element))
        self.elements[element] = (key, element)

    def extract_min(self):
        (key, element) =  heappop(self.pq)
        self.elements.pop(element)
        return element, key

    def contains(self, element):
        return element in self.elements

    def decrease_key(self, element, key):
        self.elements[element] = (key, element)
        self.pq = self.elements.values()
        heapify(self.pq)

    def insert_or_update(self, element, key):
        pass

    def remove(self, element):
        self.elements.pop(element)
        self.pq = self.elements.values()
        heapify(self.pq)
