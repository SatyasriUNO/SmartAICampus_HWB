# backend/social.py

from backend.database import (
    get_student_profile,
    get_all_students,
    get_student_clubs,
    get_all_events
)
# FIX: import _recall from memory.recall — NOT from backend.agent (circular import)
from memory.recall import _recall, get_interest_memory
from backend.llm import call_llm_structured


# ─────────────────────────────────────────────
# INTEREST OVERLAP CALCULATOR
# ─────────────────────────────────────────────

def calculate_interest_overlap(student_a_id: str, student_b_id: str) -> dict:
    profile_a = get_student_profile(student_a_id)
    profile_b = get_student_profile(student_b_id)
    if not profile_a or not profile_b:
        return {"overlap_score": 0.0, "shared_interests": [], "shared_clubs": []}

    interests_a = set(profile_a.interests)
    interests_b = set(profile_b.interests)
    shared_interests = list(interests_a & interests_b)

    clubs_a = set(profile_a.enrolled_clubs)
    clubs_b = set(profile_b.enrolled_clubs)
    shared_clubs = list(clubs_a & clubs_b)

    events_a = set(profile_a.registered_events)
    events_b = set(profile_b.registered_events)
    shared_events = list(events_a & events_b)

    max_interests = max(len(interests_a), len(interests_b), 1)
    max_clubs = max(len(clubs_a), len(clubs_b), 1)
    max_events = max(len(events_a), len(events_b), 1)

    interest_score = len(shared_interests) / max_interests * 0.5
    club_score = len(shared_clubs) / max_clubs * 0.3
    event_score = len(shared_events) / max_events * 0.2
    overlap_score = round(interest_score + club_score + event_score, 2)

    return {
        "overlap_score": overlap_score,
        "shared_interests": shared_interests,
        "shared_clubs": shared_clubs,
        "shared_events": shared_events
    }


# ─────────────────────────────────────────────
# MEMORY BASED OVERLAP
# ─────────────────────────────────────────────

def calculate_memory_overlap(student_a_id, student_b_id):
    import json
    memory_a = get_interest_memory(student_a_id)
    memory_b = get_interest_memory(student_b_id)
    prompt = f"""
Compare two students' behavioral memories to find overlap.
Student A memory:
{memory_a}
Student B memory:
{memory_b}
Return ONLY a JSON object:
{{
  "overlap_score": 0.0,
  "shared_themes": [],
  "connection_angle": "",
  "bridge_activity": ""
}}
Return ONLY the JSON. No explanation.
"""
    try:
        raw = call_llm_structured(prompt)
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {"overlap_score": 0.0, "shared_themes": [], "connection_angle": "", "bridge_activity": ""}


# ─────────────────────────────────────────────
# BRIDGE SUGGESTION GENERATOR
# ─────────────────────────────────────────────

def generate_bridge_suggestion(student_id: str, overlap: dict, memory_overlap: dict) -> str | None:
    shared_interests = overlap.get("shared_interests", [])
    shared_clubs = overlap.get("shared_clubs", [])
    bridge_activity = memory_overlap.get("bridge_activity", "")

    all_events = get_all_events()
    bridge_event = None
    for event in all_events:
        if event.category in shared_interests:
            bridge_event = event
            break

    if bridge_event:
        return (
            f"💡 There's an open collaborative opportunity in "
            f"{bridge_event.category} that aligns with what "
            f"you've been exploring — '{bridge_event.name}' "
            f"at {bridge_event.location}. "
            f"A few people with similar interests are joining."
        )
    if shared_clubs:
        club_names = ", ".join(shared_clubs)
        return (
            f"💡 Your club '{club_names}' has an open project "
            f"that matches exactly what you've been exploring lately. "
            f"Worth checking out."
        )
    if bridge_activity:
        return (
            f"💡 There's a {bridge_activity} opportunity on campus "
            f"that fits your current interests well."
        )
    return None


# ─────────────────────────────────────────────
# FIND HIGH OVERLAP PAIRS
# ─────────────────────────────────────────────

def find_high_overlap_students(student_id: str, threshold: float = 0.4) -> list[dict]:
    all_students = get_all_students()
    high_overlap = []
    for other in all_students:
        if other.student_id == student_id:
            continue
        overlap = calculate_interest_overlap(student_id, other.student_id)
        if overlap["overlap_score"] >= threshold:
            high_overlap.append({
                "overlap_score": overlap["overlap_score"],
                "shared_interests": overlap["shared_interests"],
                "shared_clubs": overlap["shared_clubs"],
                "shared_events": overlap["shared_events"]
            })
    high_overlap.sort(key=lambda x: x["overlap_score"], reverse=True)
    return high_overlap


# ─────────────────────────────────────────────
# SOCIAL GRAPH NUDGE ENGINE
# ─────────────────────────────────────────────

def get_social_nudges(student_id: str) -> dict:
    profile = get_student_profile(student_id)
    if not profile:
        return {"nudges": [], "overlap_count": 0, "top_shared_interests": [], "summary": "No social nudges available."}

    high_overlap_pairs = find_high_overlap_students(student_id, threshold=0.3)
    nudges = []
    all_shared_interests = []

    for pair in high_overlap_pairs[:3]:
        all_shared_interests.extend(pair["shared_interests"])
        memory_overlap = {
            "overlap_score": pair["overlap_score"],
            "shared_themes": pair["shared_interests"],
            "connection_angle": (
                f"Both interested in {', '.join(pair['shared_interests'])}"
                if pair["shared_interests"] else ""
            ),
            "bridge_activity": pair["shared_interests"][0] if pair["shared_interests"] else ""
        }
        nudge = generate_bridge_suggestion(student_id, pair, memory_overlap)
        if nudge and nudge not in nudges:
            nudges.append(nudge)

    top_shared = list(set(all_shared_interests))

    if not nudges:
        summary = "No strong social overlaps detected yet."
    elif len(nudges) == 1:
        summary = nudges[0]
    else:
        summary = (
            f"Found {len(high_overlap_pairs)} student(s) with "
            f"overlapping interests in: {', '.join(top_shared)}."
        )

    return {
        "nudges": nudges,
        "overlap_count": len(high_overlap_pairs),
        "top_shared_interests": top_shared,
        "summary": summary
    }


# ─────────────────────────────────────────────
# TWO STUDENT CONTRAST DEMO
# ─────────────────────────────────────────────

def run_contrast_demo() -> dict:
    # FIX: import run_agent here (local import) to avoid circular import at module level
    from backend.agent import run_agent
    from backend.reminders import get_smart_reminders
    from backend.recommender import get_recommendations, get_avoidance_flags
    from backend.filters import apply_all_filters

    query = "What should I do this evening?"
    results = {}

    for student_id in ["student-001", "student-002"]:
        profile = get_student_profile(student_id)
        avoidance = get_avoidance_flags(student_id)
        avoid_morning = avoidance.get("avoid_morning", False)
        recs = get_recommendations(student_id, top_n=5)
        filtered, meta = apply_all_filters(recs, student_id, avoid_morning)
        reminders = get_smart_reminders(student_id)
        nudges = get_social_nudges(student_id)
        agent_response = run_agent(student_id, query)

        results[student_id] = {
            "name": profile.name,
            "interests": profile.interests,
            "top_recommendations": [
                f"{r.event.name} ({r.event.category})" for r in filtered[:3]
            ],
            "reminder_summary": reminders.get("summary", ""),
            "social_nudge": nudges["nudges"][0] if nudges["nudges"] else None,
            "agent_response": agent_response.message,
            "exam_pressure": meta.get("exam_pressure", "low"),
        }

    return results
