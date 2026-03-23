# memory/anticipation.py

from datetime import datetime
from memory.recall import get_full_context, get_deadline_memory
from backend.llm import call_llm_structured


# ─────────────────────────────────────────────
# PROACTIVE TRIGGER TYPES
# ─────────────────────────────────────────────

TRIGGER_TYPES = {
    "deadline_urgent":   "🔴 Urgent deadline",
    "deadline_cascade":  "🚨 Deadline collision",
    "club_event_today":  "📅 Club event today",
    "peer_activity":     "👥 Peers are attending",
    "cross_opportunity": "💡 New opportunity found",
    "drift_alert":       "📈 Interest shift detected"
}


# ─────────────────────────────────────────────
# TRIGGER DETECTOR
# Reads memory + context to find what to surface
# ─────────────────────────────────────────────

def detect_proactive_triggers(
    student_id: str,
    upcoming_deadlines: list,
    upcoming_events: list,
    student_clubs: list
) -> list[dict]:
    """
    Scans all available context and returns
    a list of triggers that should fire proactively.

    Returns list of:
    {
      "type": trigger_type,
      "message": natural language message,
      "urgency": 1-5 (5 = most urgent)
    }
    """
    triggers = []
    now = datetime.now()

    # Trigger 1: critical deadlines (< 48 hours)
    for d in upcoming_deadlines:
        hours_left = (d.due_date - now).total_seconds() / 3600
        if hours_left <= 48:
            triggers.append({
                "type": "deadline_urgent",
                "message": (
                    f"🔴 '{d.title}' is due in "
                    f"{int(hours_left)} hours!"
                ),
                "urgency": 5
            })
        elif hours_left <= 120:
            triggers.append({
                "type": "deadline_urgent",
                "message": (
                    f"🟠 '{d.title}' is due in "
                    f"{d.due_date.strftime('%b %d')}."
                ),
                "urgency": 3
            })

    # Trigger 2: deadline cascade (3+ in same week)
    if len(upcoming_deadlines) >= 3:
        triggers.append({
            "type": "deadline_cascade",
            "message": (
                f"🚨 You have {len(upcoming_deadlines)} deadlines "
                f"colliding this week. Want help prioritizing?"
            ),
            "urgency": 4
        })

    # Trigger 3: club event today
    today = now.date()
    for event in upcoming_events:
        if event.event_datetime.date() == today:
            for club in student_clubs:
                if event.event_id in club.upcoming_events:
                    triggers.append({
                        "type": "club_event_today",
                        "message": (
                            f"📅 Your club '{club.name}' has "
                            f"'{event.name}' today at "
                            f"{event.event_datetime.strftime('%I:%M %p')}."
                        ),
                        "urgency": 3
                    })

    # Trigger 4: memory-based proactive check
    memory_triggers = _check_memory_triggers(student_id)
    triggers.extend(memory_triggers)

    # Sort by urgency — highest first
    triggers.sort(key=lambda t: t["urgency"], reverse=True)

    return triggers


def _check_memory_triggers(student_id: str) -> list[dict]:
    """
    Reads memory to find additional proactive triggers.
    Uses LLM to detect patterns worth surfacing.
    """
    memory = get_full_context(student_id)
    if "No memory found" in memory:
        return []

    prompt = f"""
You are a proactive campus assistant checking if there's
anything important to surface for a student.

Student memory:
{memory}

Current date/time: {datetime.now().strftime('%A %B %d, %Y %I:%M %p')}

Based on this memory, identify if there are any patterns
worth proactively mentioning to the student RIGHT NOW.

Return ONLY a JSON array:
[
  {{
    "type": "drift_alert or cross_opportunity or peer_activity",
    "message": "natural language message to show student",
    "urgency": 2
  }}
]

Rules:
- Only return triggers that are genuinely relevant NOW
- Maximum 2 memory-based triggers
- urgency: 1-3 only (database triggers handle 4-5)
- If nothing worth surfacing return []
Return ONLY the JSON array. No explanation.
"""

    try:
        import json
        raw = call_llm_structured(prompt)
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return []


# ─────────────────────────────────────────────
# PROACTIVE MESSAGE BUILDER
# Turns triggers into one clean opening message
# ─────────────────────────────────────────────

def build_proactive_message(
    student_name: str,
    triggers: list[dict]
) -> str:
    """
    Takes all triggers and builds one clean
    opening message for the agent.
    Prioritizes top 2 triggers only.
    """
    if not triggers:
        return f"Hey {student_name}! Everything looks clear for now."

    # Take top 2 by urgency
    top = triggers[:2]

    if len(top) == 1:
        return f"Hey {student_name}! {top[0]['message']}"

    parts = [t["message"] for t in top]
    return (
        f"Hey {student_name}! Quick heads up — "
        f"{parts[0]} Also: {parts[1]}"
    )


# ─────────────────────────────────────────────
# SHOULD PROACT CHECKER
# Simple boolean — should agent open proactively?
# ─────────────────────────────────────────────

def should_proact(
    student_id: str,
    upcoming_deadlines: list,
    upcoming_events: list,
    student_clubs: list
) -> bool:
    """
    Returns True if there's anything urgent
    enough to open proactively.
    """
    triggers = detect_proactive_triggers(
        student_id,
        upcoming_deadlines,
        upcoming_events,
        student_clubs
    )
    # Proact if any trigger has urgency >= 3
    return any(t["urgency"] >= 3 for t in triggers)
