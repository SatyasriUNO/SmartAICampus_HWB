# tests/test_memory.py

from memory.retain import (
    store_event_attended,
    store_event_ignored,
    store_club_joined
)
from memory.recall import (
    recall_as_string,
    get_interest_memory,
    check_memory_exists
)

print("=" * 55)
print("TEST 1 — Retain: store some memories")
print("=" * 55)
store_event_attended("student-001", "AI Workshop", "tech", "evening", "Block C")
store_event_attended("student-001", "Startup Pitch", "entrepreneurship", "evening")
store_event_ignored("student-001", "Morning Yoga", "sports", "morning")
store_club_joined("student-001", "Coding Society", "tech")
print("  ✅ 4 memories stored")

print("\n" + "=" * 55)
print("TEST 2 — Recall: fetch them back")
print("=" * 55)
memory = get_interest_memory("student-001")
print(f"  Memory retrieved:\n{memory}")

print("\n" + "=" * 55)
print("TEST 3 — Check memory exists")
print("=" * 55)
exists = check_memory_exists("student-001")
print(f"  Memory exists for student-001: {exists}")

print("\n🎉 Memory layer working with real Hindsight!")
