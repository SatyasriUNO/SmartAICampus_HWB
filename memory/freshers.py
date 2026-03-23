# memory/freshers.py

from datetime import datetime
from memory.retain import store_event_attended, store_club_joined
from memory.recall import check_memory_exists, get_interest_memory
from backend.llm import call_llm_structured


# ─────────────────────────────────────────────
# FRESHER DETECTION
# ─────────────────────────────────────────────

def get_fresher_day(join_date: datetime) -> int:
    """
    Returns how many days since student joined.
    Day 1 = first day, Day 30 = end of discovery arc.
    """
    delta = datetime.now() - join_date
    return max(1, delta.days + 1)


def is_in_discovery_mode(join_date: datetime) -> bool:
    """
    Returns True if student is in 30-day discovery window.
    """
    return get_fresher_day(join_date) <= 30


# ─────────────────────────────────────────────
# DISCOVERY ARC
# What to focus on each week
# ─────────────────────────────────────────────

DISCOVERY_ARC = {
    "week_1": {
        "days": range(1, 8),
        "focus": "clubs",
        "categories": ["tech", "arts", "cultural"],
        "goal": "Find at least one club that feels right",
        "nudge_template": (
            "You're in your first week — "
            "best time to explore clubs. "
            "Try visiting '{suggestion}' today, "
            "no commitment needed."
        )
    },
    "week_2": {
        "days": range(8, 15),
        "focus": "spaces",
        "categories": ["entrepreneurship", "sports"],
        "goal": "Discover campus spaces and new activity types",
        "nudge_template": (
            "Week 2 — time to explore beyond your comfort zone. "
            "'{suggestion}' is happening today. "
            "Even showing up counts."
        )
    },
    "week_3": {
        "days": range(15, 22),
        "focus": "peers",
        "categories": ["cultural", "arts"],
        "goal": "Find people with similar interests",
        "nudge_template": (
            "You're settling in nicely. "
            "'{suggestion}' is a great way to "
            "meet people who think like you."
        )
    },
    "week_4": {
        "days": range(22, 31),
        "focus": "cross_interest",
        "categories": [],
        "goal": "First real personalized recommendations",
        "nudge_template": (
            "You've explored a lot in your first month. "
            "Based on what you've engaged with, "
            "'{suggestion}' seems like a perfect next step."
        )
    }
}


def get_current_week(day_number: int) -> str:
    """Returns which week arc the student is in."""
    for week, config in DISCOVERY_ARC.items():
        if day_number in config["days"]:
            return week
    return "week_4"


# ─────────────────────────────────────────────
# DAILY NUDGE GENERATOR
# One nudge per day — don't overwhelm freshers
# ─────────────────────────────────────────────

def get_daily_nudge(
    student_id: str,
    join_date: datetime,
    available_events: list[dict]
) -> dict:
    """
    Returns ONE nudge for today based on
    where the student is in their discovery arc.

    Returns:
    {
      "day": int,
      "week": str,
      "focus": str,
      "nudge": str,
      "event": dict or None,
      "goal": str
    }
    """
    day = get_fresher_day(join_date)
    week = get_current_week(day)
    arc = DISCOVERY_ARC[week]

    # Week 4 — use real cross-interest recommendations
    if week == "week_4":
        return _get_week4_nudge(student_id, day, available_events)

    # Weeks 1-3 — category-based discovery
    focus_categories = arc["categories"]
    matching_events = [
        e for e in available_events
        if e.get("category") in focus_categories
    ]

    if not matching_events:
        return {
            "day": day,
            "week": week,
            "focus": arc["focus"],
            "nudge": (
                f"Day {day} — explore {arc['focus']} today. "
                f"Check the campus notice board for options."
            ),
            "event": None,
            "goal": arc["goal"]
        }

    # Pick one event — don't overwhelm
    suggestion = matching_events[0]
    nudge = arc["nudge_template"].format(
        suggestion=suggestion["name"]
    )

    return {
        "day": day,
        "week": week,
        "focus": arc["focus"],
        "nudge": nudge,
        "event": suggestion,
        "goal": arc["goal"]
    }


def _get_week4_nudge(
    student_id: str,
    day: int,
    available_events: list[dict]
) -> dict:
    """
    Week 4 nudge — personalized based on
    what student engaged with in weeks 1-3.
    """
    memory = get_interest_memory(student_id)
    has_memory = check_memory_exists(student_id)

    if not has_memory or not available_events:
        return {
            "day": day,
            "week": "week_4",
            "focus": "cross_interest",
            "nudge": (
                "You've explored a lot in your first month! "
                "The assistant now knows you well enough to make "
                "real recommendations. Ask me anything."
            ),
            "event": None,
            "goal": DISCOVERY_ARC["week_4"]["goal"]
        }

    events_str = "\n".join(
        f"- {e['name']} (category: {e['category']})"
        for e in available_events
    )

    prompt = f"""
A fresher student has completed 3 weeks of campus exploration.
Based on their memory, suggest the single best next event.

Student memory (what they've explored):
{memory}

Available events:
{events_str}

Return ONLY a JSON object:
{{
  "event_name": "...",
  "reason": "one sentence why this fits them perfectly"
}}

Base the reason on what they've actually done in their memory.
Return ONLY the JSON. No explanation.
"""

    try:
        import json
        raw = call_llm_structured(prompt)
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)

        matched_event = next(
            (e for e in available_events
             if e["name"] == result.get("event_name")),
            available_events[0]
        )

        return {
            "day": day,
            "week": "week_4",
            "focus": "cross_interest",
            "nudge": (
                f"Based on your first month — "
                f"{result.get('reason', 'this looks perfect for you.')} "
                f"Check out '{matched_event['name']}'."
            ),
            "event": matched_event,
            "goal": DISCOVERY_ARC["week_4"]["goal"]
        }
    except Exception:
        return {
            "day": day,
            "week": "week_4",
            "focus": "cross_interest",
            "nudge": "You're ready for real recommendations now. Ask me anything!",
            "event": None,
            "goal": DISCOVERY_ARC["week_4"]["goal"]
        }


# ─────────────────────────────────────────────
# MEMORY BUILDER FOR FRESHERS
# Stores engagement/ignore for discovery arc
# ─────────────────────────────────────────────

def record_fresher_engagement(
    student_id: str,
    event_name: str,
    category: str,
    engaged: bool
) -> None:
    """
    Records whether fresher engaged with
    a nudge or ignored it.
    Builds memory progressively over 30 days.
    """
    if engaged:
        store_event_attended(
            student_id=student_id,
            event_name=event_name,
            category=category,
            time_of_day="discovery_arc"
        )
    else:
        from memory.retain import store_event_ignored
        store_event_ignored(
            student_id=student_id,
            event_name=event_name,
            category=category,
            time_of_day="discovery_arc"
        )


# ─────────────────────────────────────────────
# GRADUATION CHECK
# When fresher mode ends
# ─────────────────────────────────────────────

def has_graduated_discovery(join_date: datetime) -> bool:
    """
    Returns True when 30-day discovery is complete.
    After this, full recommendation engine takes over.
    """
    return get_fresher_day(join_date) > 30


def get_graduation_message(student_id: str) -> str:
    """
    Message shown when student exits fresher mode.
    """
    memory = get_interest_memory(student_id)

    prompt = f"""
A student has just completed their 30-day campus discovery journey.
Based on their memory, write a short 2-sentence graduation message
that acknowledges what they explored and hints at what's next.

Student memory:
{memory}

Sound warm and personal, like a senior student talking to a junior.
Return ONLY the 2-sentence message.
"""

    try:
        return call_llm_structured(prompt).strip()
    except Exception:
        return (
            "You've completed your first month — "
            "the assistant now knows you well enough "
            "to make genuinely useful recommendations. "
            "Welcome to the full experience!"
        )
