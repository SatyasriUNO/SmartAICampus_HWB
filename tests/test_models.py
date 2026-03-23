# tests/test_models.py

from datetime import datetime
from backend.models import StudentProfile, Event, Deadline, MemoryEntry, get_time_of_day

# Test student
s = StudentProfile(
    student_id="student-001",
    name="Arjun",
    year=1,
    enrolled_clubs=["coding-society"],
    registered_events=["ai-workshop-01"],
    academic_deadlines=["dl-001"],
    join_date=datetime(2025, 8, 1),
    interests=["tech", "entrepreneurship"]
)
print("✅ Student:", s.name, "| Year:", s.year)

# Test event
e = Event(
    event_id="ai-workshop-01",
    name="AI & ML Workshop",
    category="tech",
    event_datetime=datetime(2025, 3, 25, 18, 0),
    location="Block C Seminar Hall",
    attendees=["student-001", "student-002"],
    duration_minutes=120,
    is_morning=False
)
print("✅ Event:", e.name, "| Category:", e.category)

# Test memory entry
m = MemoryEntry(
    student_id="student-001",
    action="attended",
    target_type="event",
    target_name="AI & ML Workshop",
    category="tech",
    timestamp=datetime.now(),
    time_of_day=get_time_of_day(datetime.now())
)
print("✅ Memory:", m.action, m.target_name, "| Time:", m.time_of_day)

print("\n🎉 All models working correctly!")
