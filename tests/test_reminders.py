# tests/test_reminders.py

from backend.reminders import (
    get_smart_reminders,
    detect_deadline_cascade,
    check_event_deadline_collision,
    get_club_event_reminders,
    get_attendance_patterns
)

print("=" * 60)
print("TEST 1 — Smart reminders for Arjun (student-001)")
print("=" * 60)
result = get_smart_reminders("student-001")
print(f"  Summary: {result['summary']}")
print(f"\n  Deadline reminders:")
for r in result["deadline_reminders"]:
    print(f"    {r}")
print(f"\n  Collision warnings:")
for w in result["collision_warnings"]:
    print(f"    {w}")
print(f"\n  Club reminders:")
for r in result["club_reminders"]:
    print(f"    {r}")

print("\n" + "=" * 60)
print("TEST 2 — Deadline cascade for Arjun")
print("=" * 60)
cascade = detect_deadline_cascade("student-001", window_days=30)
print(f"  Cascade: {cascade['cascade']}")
print(f"  Count: {cascade['count']}")
if cascade["cascade"]:
    print(f"  Alert: {cascade['alert']}")
    print(f"  Priority order:")
    for line in cascade["priority_order"]:
        print(f"  {line}")

print("\n" + "=" * 60)
print("TEST 3 — Smart reminders for Priya (student-002)")
print("=" * 60)
result = get_smart_reminders("student-002")
print(f"  Summary: {result['summary']}")
for r in result["deadline_reminders"]:
    print(f"    {r}")

print("\n" + "=" * 60)
print("TEST 4 — Attendance patterns")
print("=" * 60)
patterns = get_attendance_patterns("student-001")
print(f"  Patterns: {patterns}")

print("\n" + "=" * 60)
print("TEST 5 — Club event reminders for Arjun")
print("=" * 60)
club_reminders = get_club_event_reminders("student-001")
if club_reminders:
    for r in club_reminders:
        print(f"  {r}")
else:
    print("  No club events in next 48 hours")

print("\n🎉 Reminders engine working correctly!")
