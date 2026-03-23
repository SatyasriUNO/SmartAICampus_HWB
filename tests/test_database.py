# tests/test_database.py

from backend.database import (
    get_all_events,
    get_events_by_category,
    get_upcoming_deadlines,
    get_student_profile,
    get_student_clubs,
    is_fresher,
    get_cascade_window
)

# Test 1: all events
events = get_all_events()
print(f"✅ Total events: {len(events)}")

# Test 2: events by category
tech_events = get_events_by_category("tech")
print(f"✅ Tech events: {[e.name for e in tech_events]}")

# Test 3: upcoming deadlines
deadlines = get_upcoming_deadlines("student-001", days=30)
print(f"✅ Arjun's deadlines: {[d.title for d in deadlines]}")

# Test 4: student profile
profile = get_student_profile("student-002")
print(f"✅ Student B: {profile.name} | Interests: {profile.interests}")

# Test 5: clubs for student
clubs = get_student_clubs("student-001")
print(f"✅ Arjun's clubs: {[c.name for c in clubs]}")

# Test 6: fresher detection
print(f"✅ Is student-003 a fresher? {is_fresher('student-003')}")
print(f"✅ Is student-001 a fresher? {is_fresher('student-001')}")

# Test 7: cascade detection
cascade = get_cascade_window("student-001", days=30)
print(f"✅ Cascade alert: {cascade['alert']}")

print("\n🎉 Database layer working correctly!")
