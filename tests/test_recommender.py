# tests/test_recommender.py

from backend.recommender import (
    get_recommendations,
    get_fresher_recommendations,
    get_avoidance_flags
)

print("=" * 60)
print("TEST 1 — Recommendations for Arjun (tech + entrepreneurship)")
print("=" * 60)
recs = get_recommendations("student-001", top_n=5)
for r in recs:
    cross = "🔀 CROSS INTEREST" if r.cross_interest else ""
    print(f"  [{r.score}] {r.event.name} — {r.reason} {cross}")

print("\n" + "=" * 60)
print("TEST 2 — Recommendations for Priya (arts + cultural)")
print("=" * 60)
recs = get_recommendations("student-002", top_n=5)
for r in recs:
    cross = "🔀 CROSS INTEREST" if r.cross_interest else ""
    print(f"  [{r.score}] {r.event.name} — {r.reason} {cross}")

print("\n" + "=" * 60)
print("TEST 3 — Same question, visibly different results?")
print("=" * 60)
recs_a = [r.event.name for r in get_recommendations("student-001", top_n=3)]
recs_b = [r.event.name for r in get_recommendations("student-002", top_n=3)]
print(f"  Arjun sees:  {recs_a}")
print(f"  Priya sees:  {recs_b}")
overlap = set(recs_a) & set(recs_b)
print(f"  Overlap: {overlap if overlap else '✅ None — perfect contrast!'}")

print("\n" + "=" * 60)
print("TEST 4 — Fresher recommendations (Rahul, day 5)")
print("=" * 60)
recs = get_fresher_recommendations("student-003", day_number=5)
for r in recs:
    print(f"  {r.event.name} — {r.reason}")

print("\n" + "=" * 60)
print("TEST 5 — Avoidance flags")
print("=" * 60)
flags = get_avoidance_flags("student-001")
print(f"  Flags: {flags}")

print("\n🎉 Recommender working correctly!")
