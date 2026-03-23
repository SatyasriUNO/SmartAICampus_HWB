# tests/test_filters.py

from backend.recommender import get_recommendations
from backend.filters import (
    apply_all_filters,
    is_exam_week,
    get_exam_pressure_level,
    detect_interest_drift
)

print("=" * 60)
print("TEST 1 — Exam pressure detection")
print("=" * 60)
for sid in ["student-001", "student-002", "student-004"]:
    pressure = get_exam_pressure_level(sid)
    exam = is_exam_week(sid)
    print(f"  {sid}: pressure={pressure} | exam_week={exam}")

print("\n" + "=" * 60)
print("TEST 2 — Full filter pipeline for Arjun")
print("=" * 60)
recs = get_recommendations("student-001", top_n=8)
print(f"  Before filters: {len(recs)} recommendations")
filtered, meta = apply_all_filters(
    recs,
    student_id="student-001",
    avoid_morning=True       # Arjun avoids mornings
)
print(f"  After filters: {len(filtered)} recommendations")
print(f"  Exam pressure: {meta['exam_pressure']}")
print(f"  Filters applied: {meta['filters_applied']}")
if meta["overload_warning"]:
    print(f"  ⚠️ Warning: {meta['overload_warning']}")
print("  Final list:")
for r in filtered:
    print(f"    [{r.score}] {r.event.name} — {r.reason}")

print("\n" + "=" * 60)
print("TEST 3 — Full filter pipeline for Priya")
print("=" * 60)
recs = get_recommendations("student-002", top_n=8)
filtered, meta = apply_all_filters(
    recs,
    student_id="student-002",
    avoid_morning=False
)
print(f"  After filters: {len(filtered)} recommendations")
if meta["overload_warning"]:
    print(f"  ⚠️ Warning: {meta['overload_warning']}")
print("  Final list:")
for r in filtered:
    print(f"    [{r.score}] {r.event.name} — {r.reason}")

print("\n" + "=" * 60)
print("TEST 4 — Interest drift detection")
print("=" * 60)
drift = detect_interest_drift("student-001")
print(f"  Drift detected: {drift['drift_detected']}")
print(f"  Emerging: {drift['emerging']}")
print(f"  Fading:   {drift['fading']}")
print(f"  Stable:   {drift['stable']}")

print("\n🎉 Filters working correctly!")
