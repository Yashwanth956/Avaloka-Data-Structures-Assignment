"""Run reproducible tests against Assignment_Avaloka_Solutions.py."""
import importlib.util
import random
from collections import OrderedDict
from pathlib import Path

SOURCE = Path(__file__).with_name('Assignment_Avaloka_Solutions.py')
spec = importlib.util.spec_from_file_location('avaloka_solutions', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
LRUCache = module.LRUCache
can_attend_all = module.can_attend_all
min_rooms_required = module.min_rooms_required
results = []
checks = 0

def check(actual, expected, label):
    global checks
    checks += 1
    if actual != expected:
        raise AssertionError(f'{label}: expected {expected!r}, got {actual!r}')

def group(name, fn):
    before = checks
    fn()
    results.append((name, checks - before))

def oracle_rooms(events):
    # Half-open intervals [start, end): a meeting ending at 10
    # releases its room for any meeting starting at 10.
    changes = []
    for start, end in events:
        changes.extend([(start, 1), (end, -1)])
    changes.sort()  # -1 (end) before +1 (start) for equal times.
    current = maximum = 0
    for _, delta in changes:
        current += delta
        maximum = max(maximum, current)
    return maximum

def test_main_scenarios():
    cache = LRUCache(2)
    cache.put(1, 10); cache.put(2, 20)
    check(cache.get(1), 10, 'get existing')
    cache.put(3, 30)
    check(cache.get(2), -1, 'evict LRU')
    cache.put(1, 15)
    check(cache.get(1), 15, 'update')
    for meetings, expected_attend, expected_rooms in [
        ([(9, 10), (10, 11), (11, 12)], True, 1),
        ([(9, 11), (10, 12), (11, 13)], False, 2),
        ([], True, 0),
    ]:
        check(can_attend_all(meetings), expected_attend, f'attend {meetings}')
        check(min_rooms_required(meetings), expected_rooms, f'rooms {meetings}')

def test_cache_edges():
    cases = [
        (1, [('get', 'x', -1), ('put', 'x', None), ('get', 'x', None), ('put', 'y', 0), ('get', 'x', -1), ('get', 'y', 0)]),
        (2, [('put', -1, 'minus'), ('put', 0, 0), ('get', -1, 'minus'), ('put', 0, 10), ('put', 2, 3), ('get', -1, -1), ('get', 0, 10)]),
        (3, [('put', 'same', 1), ('put', 'same', 2), ('get', 'same', 2), ('get', 'missing', -1)]),
    ]
    for capacity, operations in cases:
        cache = LRUCache(capacity)
        for op in operations:
            if op[0] == 'put': cache.put(op[1], op[2])
            else: check(cache.get(op[1]), op[2], f'cache edge {capacity} {op}')
    for bad in [0, -1, -10]:
        try: LRUCache(bad)
        except ValueError: check(True, True, f'bad capacity {bad}')
        else: raise AssertionError(f'Capacity {bad} did not raise ValueError')

def test_event_edges():
    cases = [
        ([(10,11)], 1),
        ([(11,12),(9,10),(10,11)], 1),
        ([(9,12),(9,12),(9,12)], 3),
        ([(9,20),(10,11),(12,13),(13,15)], 2),
        ([(1,9),(2,8),(3,7),(4,6)], 4),
        ([(1,2),(3,4),(5,6)], 1),
        ([(1,3),(3,5),(5,7),(2,4)], 2),
        ([(-5,-3),(-3,0),(0,5)], 1),
        ([(9.5,10.0),(10.0,11.5),(9.8,10.2)], 2),
        ([(5,9),(5,7),(7,10),(9,10)], 2),
    ]
    for events, expected in cases:
        check(min_rooms_required(events), expected, f'rooms edge {events}')
        check(can_attend_all(events), expected <= 1, f'attend edge {events}')

def test_lru_randomized():
    for seed in range(50):
        rng = random.Random(seed)
        capacity = rng.randint(1, 12)
        cache = LRUCache(capacity)
        oracle = OrderedDict()
        for idx in range(500):
            key = rng.randint(-5, 25)
            if rng.random() < 0.54:
                value = rng.choice([None, 0, False, '', idx, -idx])
                cache.put(key, value)
                if key in oracle:
                    oracle[key] = value
                    oracle.move_to_end(key)
                else:
                    if len(oracle) == capacity:
                        oracle.popitem(last=False)
                    oracle[key] = value
            else:
                actual = cache.get(key)
                expected = oracle.get(key, -1)
                if key in oracle: oracle.move_to_end(key)
                check(actual, expected, f'lru random seed={seed} i={idx} key={key}')
            # Verify linked list recency order and map after EVERY operation.
            nodes = []
            cur = cache.head.next
            while cur is not cache.tail:
                if len(nodes) > capacity:
                    raise AssertionError(f'Unexpected linked list cycle seed={seed} i={idx}')
                check(cur.prev.next is cur and cur.next.prev is cur, True, f'broken links seed={seed} i={idx}')
                check(cache.cache[cur.key] is cur, True, f'orphan node seed={seed} i={idx}')
                nodes.append(cur.key)
                cur = cur.next
            check(nodes, list(oracle.keys()), f'recency order seed={seed} i={idx}')
            check(len(cache.cache), len(oracle), f'cache size seed={seed} i={idx}')

def test_event_randomized():
    rng = random.Random(20261022)
    for index in range(15000):
        n = rng.randint(0, 20)
        events = []
        for _ in range(n):
            start = rng.randint(-30, 40)
            end = start + rng.randint(1, 15)
            events.append((start, end))
        rng.shuffle(events)
        expected = oracle_rooms(events)
        check(min_rooms_required(events), expected, f'rooms randomized {index}: {events}')
        check(can_attend_all(events), expected <= 1, f'attend randomized {index}: {events}')
        
def test_performance_smoke():
    # Not a formal benchmark/proof; covers large inputs for obvious slowdowns.
    cache = LRUCache(10000)
    for key in range(100000): cache.put(key, key+1)
    check(cache.get(99999), 100000, 'large cache last')
    check(cache.get(0), -1, 'large cache eviction')
    events = [(i,i+1) for i in range(20000)]
    check(can_attend_all(events), True, 'large adjacent schedule')
    check(min_rooms_required(events), 1, 'large adjacent schedule rooms')
    overlapping = [(0,10) for _ in range(10000)]
    check(min_rooms_required(overlapping), 10000, 'large overlapping rooms')

if __name__ == '__main__':
    group('Assignment examples', test_main_scenarios)
    group('LRU edge cases', test_cache_edges)
    group('Scheduler edge cases', test_event_edges)
    group('LRU randomized + structural checks (25,000 operations)', test_lru_randomized)
    group('Scheduler randomized vs independent sweep-line reference (15,000 schedules)', test_event_randomized)
    group('Large input smoke checks', test_performance_smoke)
    print('AVALOKA ASSIGNMENT TEST REPORT')
    print('-------------------------------------')
    for name, n in results: print(f'PASS  {name}: {n:,} checks')
    print(f'\nTOTAL: {checks:,} checks passed; 0 failures')
    print('Note: Valid scheduler inputs assumed to have start < end.')
    print('Note: Concurrency not tested; submitted LRU is not thread-safe.')
