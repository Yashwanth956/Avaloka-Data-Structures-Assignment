# Avaloka - Data Structures & Systems Design

**Candidate:** Bolishetty Yashwanth  
**Role:** AI / Multi-Agent Systems Intern

This repository contains my Python solutions to two assignment problems:

1. **LRU Cache:** A cache supporting `get(key)` and `put(key, value)` in expected O(1) time using a dictionary and doubly linked list.
2. **Event Scheduler:** Checks whether meetings overlap and calculates the minimum number of meeting rooms required. Meetings ending exactly when another starts can share a room.

## Files

- `Assignment_Avaloka_Solutions.py` — implementations and basic assertions.
- `test_avaloka_assignment.py` — additional tests.

## How to run

Python 3 is required. No third-party packages are needed.

```bash
python Assignment_Avaloka_Solutions.py
python test_avaloka_assignment.py
```

The solutions file checks examples with `assert`, so it does not print output when those checks pass.

## Notes

- LRU cache operations: expected O(1) time, O(capacity) storage.
- Checking whether meetings overlap: O(n log n) time due to sorting.
- Calculating meeting rooms: O(n log n) time using a min-heap.
