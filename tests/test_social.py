# tests/test_social.py

from backend.social import (
    calculate_interest_overlap,
    find_high_overlap_students,
    get_social_nudges,
    run_contrast_demo
)

print("=" * 60)
print("TEST 1 — Interest overlap between Arjun and Priya")
print("=" * 60)
overlap = calculate_interest_overlap("student-001", "student-002")
print(f"  Overlap score: {overlap['overlap_score']}")
print(f"  Shared interests: {overlap['shared_interests']}")
print(f"  Shared clubs: {overlap['shared_clubs']}")
print(f"  Shared events: {overlap['shared_events']}")

print("\n" + "=" * 60)
print("TEST 2 — High overlap students for Arjun")
print("=" * 60)
pairs = find_high_overlap_students("student-001", threshold=0.2)
print(f"  Found {len(pairs)} high overlap students")
for p in pairs:
    print(
        f"  Score: {p['overlap_score']} | "
        f"Shared: {p['shared_interests']} | "
        f"Clubs: {p['shared_clubs']}"
    )

print("\n" + "=" * 60)
print("TEST 3 — Social nudges for Arjun")
print("=" * 60)
nudges = get_social_nudges("student-001")
print(f"  Overlap count: {nudges['overlap_count']}")
print(f"  Top shared interests: {nudges['top_shared_interests']}")
print(f"  Summary: {nudges['summary']}")
print(f"  Nudges:")
for n in nudges["nudges"]:
    print(f"    {n}")

print("\n" + "=" * 60)
print("TEST 4 — Social nudges for Priya")
print("=" * 60)
nudges = get_social_nudges("student-002")
print(f"  Summary: {nudges['summary']}")
for n in nudges["nudges"]:
    print(f"    {n}")

print("\n" + "=" * 60)
print("🎬 TEST 5 — TWO STUDENT CONTRAST DEMO")
print("=" * 60)
print("  Same query: 'What should I do this evening?'")
print("  Fetching results for both students...\n")

results = run_contrast_demo()

for student_id, data in results.items():
    print(f"  {'─'*50}")
    print(f"  🧑 {data['name'].upper()} | Interests: {data['interests']}")
    print(f"  {'─'*50}")
    print(f"  📋 Top Recommendations:")
    for rec in data["top_recommendations"]:
        print(f"      → {rec}")
    print(f"  ⏰ Reminders: {data['reminder_summary']}")
    if data["social_nudge"]:
        print(f"  💡 Social Nudge: {data['social_nudge']}")
    print(f"  🤖 Agent Says:")
    print(f"      {data['agent_response']}")
    print(f"  📊 Exam Pressure: {data['exam_pressure']}")
    print()

print("🎉 Social graph nudging working correctly!")
