class Node:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = {}
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_recent(self, node):
        last = self.tail.prev
        last.next = node
        node.prev = last
        node.next = self.tail
        self.tail.prev = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_recent(node)
        return node.value

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_recent(node)
            return

        if len(self.cache) == self.capacity:
            oldest = self.head.next
            self._remove(oldest)
            del self.cache[oldest.key]

        node = Node(key, value)
        self.cache[key] = node
        self._add_recent(node)

import heapq
def can_attend_all(events):
    meetings = sorted(events)
    for i in range(1, len(meetings)):
        if meetings[i][0] < meetings[i - 1][1]:
            return False
    return True

def min_rooms_required(events):
    meetings = sorted(events)
    end_times = []
    max_rooms = 0

    for start, end in meetings:
        # These rooms are free before this meeting starts.
        while end_times and end_times[0] <= start:
            heapq.heappop(end_times)

        heapq.heappush(end_times, end)
        max_rooms = max(max_rooms, len(end_times))

    return max_rooms
    
if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    assert cache.get(1) == 10
    cache.put(3, 30)       # Key 2 gets removed.
    assert cache.get(2) == -1
    cache.put(1, 15)       # Updating a key also makes it recent.
    assert cache.get(1) == 15

    adjacent = [(9, 10), (10, 11), (11, 12)]
    overlap = [(9, 11), (10, 12), (11, 13)]
    assert can_attend_all(adjacent) is True
    assert min_rooms_required(adjacent) == 1
    assert can_attend_all(overlap) is False
    assert min_rooms_required(overlap) == 2
    assert can_attend_all([]) is True
    assert min_rooms_required([]) == 0
