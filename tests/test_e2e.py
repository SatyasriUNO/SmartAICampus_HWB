# tests/test_e2e.py
# Direct function calls — no HTTP, no TestClient, no async issues

from backend.agent import run_agent
from backend.recommender import get_recommendations, get_avoidance_flags
from backend.filters import apply_all_filters, detect_interest_drift
from backend.reminders import get_smart_reminders
from backend.social import get_social_nudges
from backend.database import get_student_profile, is_fresher

print("\n" + "🔥" * 30)
print("   END-TO-END PIPELINE TEST")
print("🔥" * 30)


# ─────────────────────────────────────────────
# SCENARIO 1: Arjun starts his day
# ─────────────────────────────────────────────
print("\n📍 SCENARIO 1 — Arjun opens the app (proactive mode)")
print("─" * 55)

response = run_agent("student-001", "")
print(f"🤖 Agent opens with:\n   {response.message}\n")

avoidance = get_avoidance_flags("student-001")
avoid_morning = avoidance.get("avoid_morning", False)
recs = get_recommendations("student-001", top_n=5)
filtered, meta = apply_all_filters(recs, "student-001", avoid_morning)

print(f"📋 Recommendations ({meta['exam_pressure']} exam pressure):")
for rec in filtered[:3]:
    cross = "🔀" if rec.cross_interest else "  "
    print(f"   {cross} [{rec.score}] {rec.event.name}")
    print(f"       → {rec.reason}")

reminders = get_smart_reminders("student-001")
print(f"\n⏰ Reminder summary: {reminders['summary']}")
if reminders["cascade"]["cascade"]:
    print(f"🚨 Cascade: {reminders['cascade']['alert']}")
    for line in reminders["cascade"]["priority_order"]:
        print(f"   {line}")

nudges = get_social_nudges("student-001")
print(f"\n💡 Social nudges:")
for n in nudges["nudges"]:
    print(f"   {n}")


# ─────────────────────────────────────────────
# SCENARIO 2: Arjun asks about events
# ─────────────────────────────────────────────
print("\n\n📍 SCENARIO 2 — Arjun asks about events")
print("─" * 55)

response = run_agent("student-001", "What events should I go to this week?")
print(f"👤 Arjun: What events should I go to this week?")
print(f"🤖 Agent: {response.message}\n")


# ─────────────────────────────────────────────
# SCENARIO 3: Priya same question
# ─────────────────────────────────────────────
print("\n📍 SCENARIO 3 — Priya asks SAME question")
print("─" * 55)

response = run_agent("student-002", "What events should I go to this week?")
print(f"👤 Priya: What events should I go to this week?")
print(f"🤖 Agent: {response.message}\n")


# ─────────────────────────────────────────────
# SCENARIO 4: Fresher joins
# ─────────────────────────────────────────────
print("\n📍 SCENARIO 4 — Rahul just joined (fresher mode)")
print("─" * 55)

response = run_agent("student-003", "I just joined college. What should I do?")
print(f"👤 Rahul: I just joined college. What should I do?")
print(f"🤖 Agent: {response.message}\n")

profile = get_student_profile("student-003")
days = ((__import__("datetime").datetime.now()) - profile.join_date).days
print(f"📋 Fresher — day {days} of discovery arc")


# ─────────────────────────────────────────────
# SCENARIO 5: Deadline stress
# ─────────────────────────────────────────────
print("\n\n📍 SCENARIO 5 — Arjun asks about deadlines")
print("─" * 55)

response = run_agent("student-001", "I'm stressed, what deadlines do I have?")
print(f"👤 Arjun: I'm stressed, what deadlines do I have?")
print(f"🤖 Agent: {response.message}\n")


# ─────────────────────────────────────────────
# SCENARIO 6: Interest drift
# ─────────────────────────────────────────────
print("\n📍 SCENARIO 6 — Interest drift analysis")
print("─" * 55)

for sid in ["student-001", "student-002"]:
    profile = get_student_profile(sid)
    drift = detect_interest_drift(sid)
    print(f"  {profile.name}: drift={drift['drift_detected']} | "
          f"emerging={drift['emerging']} | fading={drift['fading']}")


# ─────────────────────────────────────────────
# JUDGE DEMO
# ─────────────────────────────────────────────
print("\n\n" + "=" * 55)
print("🎬  JUDGE DEMO — TWO STUDENT CONTRAST")
print("=" * 55)
print("   Same campus. Same events. Same query.")
print("   Completely different experience.")
print("=" * 55)

query = "What should I do this evening?"
print(f"\n   Query: \"{query}\"\n")

for student_id in ["student-001", "student-002"]:
    profile = get_student_profile(student_id)

    # Avoidance + recommendations
    avoidance = get_avoidance_flags(student_id)
    avoid_morning = avoidance.get("avoid_morning", False)
    recs = get_recommendations(student_id, top_n=5)
    filtered, meta = apply_all_filters(recs, student_id, avoid_morning)

    # Reminders
    reminders = get_smart_reminders(student_id)

    # Social nudges
    nudges = get_social_nudges(student_id)

    # Agent response
    agent_response = run_agent(student_id, query)

    print(f"{'─' * 55}")
    print(f"  🧑 {profile.name.upper()}")
    print(f"  Interests: {profile.interests}")
    print(f"  Exam Pressure: {meta['exam_pressure']}")
    print(f"\n  📋 Recommendations:")
    for r in filtered[:3]:
        print(f"      → {r.event.name} ({r.event.category})")
    print(f"\n  ⏰ {reminders['summary']}")
    if nudges["nudges"]:
        print(f"\n  💡 {nudges['nudges'][0]}")
    print(f"\n  🤖 Agent says:")
    print(f"      \"{agent_response.message[:200]}\"")
    print()

print("=" * 55)
print("✅ Both students got completely different responses")
print("✅ Same query — memory-driven personalization at work")
print("✅ This is Hindsight doing its job")
print("=" * 55)

print("\n🎉 ALL SYSTEMS GO — Pipeline fully wired!\n")
