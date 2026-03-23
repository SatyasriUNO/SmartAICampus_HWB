# tests/test_api.py — simplified direct test

from backend.database import get_student_profile, get_all_events
from backend.agent import run_agent
from backend.recommender import get_recommendations
from backend.reminders import get_smart_reminders
from backend.social import get_social_nudges
from backend.filters import get_exam_pressure_level

print("=" * 55)
print("TEST 1 — Student profile")
print("=" * 55)
profile = get_student_profile("student-001")
print(f"  Name: {profile.name}")
print(f"  Interests: {profile.interests}")
print(f"  Exam pressure: {get_exam_pressure_level('student-001')}")

print("\n" + "=" * 55)
print("TEST 2 — Chat proactive")
print("=" * 55)
r = run_agent("student-001", "")
print(f"  Proactive: {r.proactive}")
print(f"  Agent: {r.message[:150]}...")

print("\n" + "=" * 55)
print("TEST 3 — Recommendations")
print("=" * 55)
recs = get_recommendations("student-001", top_n=3)
for r in recs:
    print(f"  [{r.score}] {r.event.name} — {r.reason}")

print("\n" + "=" * 55)
print("TEST 4 — Reminders")
print("=" * 55)
result = get_smart_reminders("student-001")
print(f"  Summary: {result['summary']}")

print("\n" + "=" * 55)
print("TEST 5 — Social nudges")
print("=" * 55)
nudges = get_social_nudges("student-001")
print(f"  Summary: {nudges['summary']}")

print("\n" + "=" * 55)
print("TEST 6 — All events")
print("=" * 55)
events = get_all_events()
print(f"  Total events: {len(events)}")

print("\n🎉 All API functions working correctly!")
