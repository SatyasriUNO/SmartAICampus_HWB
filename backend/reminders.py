# backend/reminders.py

from datetime import datetime, timedelta
from backend.models import Deadline
from backend.database import (
    get_upcoming_deadlines,
    get_student_profile,
    get_student_clubs,
    get_all_events,
    get_cascade_window
)
# FIX: import _recall from memory.recall — NOT from backend.agent (circular import)
from memory.recall import _recall, get_deadline_memory
from backend.llm import call_llm_structured


# ─────────────────────────────────────────────
# URGENCY CLASSIFIER
# ─────────────────────────────────────────────

def classify_urgency(deadline: Deadline) -> str:
    now = datetime.now()
    hours_left = (deadline.due_date - now).total_seconds() / 3600
    if hours_left <= 24:
        return "critical"
    elif hours_left <= 48:
        return "high"
    elif hours_left <= 120:
        return "medium"
    else:
        return "low"


def urgency_emoji(level: str) -> str:
    return {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(level, "⚪")


# ─────────────────────────────────────────────
# ATTENDANCE PATTERN READER
# ─────────────────────────────────────────────

def get_attendance_patterns(student_id: str) -> dict:
    import json
    memory = get_deadline_memory(student_id)
    prompt = f"""
Analyze this student's memory for attendance and deadline patterns.
Memory:
{memory}

Return ONLY a JSON object:
{{
  "usually_completes_on_time": true,
  "misses_club_deadlines": false,
  "ignores_reminders": false,
  "last_minute_person": false,
  "reliable_for_academic": true
}}
Return ONLY the JSON. No explanation.
"""
    try:
        raw = call_llm_structured(prompt)
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {
            "usually_completes_on_time": True,
            "misses_club_deadlines": False,
            "ignores_reminders": False,
            "last_minute_person": False,
            "reliable_for_academic": True
        }


# ─────────────────────────────────────────────
# SMART REMINDER GENERATOR
# ─────────────────────────────────────────────

def generate_reminder_message(
    deadline: Deadline,
    urgency: str,
    patterns: dict
) -> str:
    emoji = urgency_emoji(urgency)
    time_left = deadline.due_date - datetime.now()
    hours = int(time_left.total_seconds() / 3600)
    days = time_left.days

    if hours <= 24:
        time_str = f"in {hours} hours"
    elif days == 1:
        time_str = "tomorrow"
    else:
        time_str = f"in {days} days"

    base = f"{emoji} {deadline.title} is due {time_str}"

    if urgency == "critical" and patterns.get("last_minute_person"):
        base += " — you usually cut it close, don't miss this one."
    elif urgency == "critical":
        base += " — act now."
    elif urgency == "high" and patterns.get("ignores_reminders"):
        base += " — you've ignored reminders before. This one matters."
    elif urgency == "medium" and patterns.get("usually_completes_on_time"):
        base += " — you're usually on top of these, just a heads up."
    elif deadline.type == "internship":
        base += " — don't let this one slip, internship windows are short."
    elif deadline.type == "fest":
        base += " — registration closes and won't reopen."

    return base


# ─────────────────────────────────────────────
# DEADLINE CASCADE DETECTOR
# ─────────────────────────────────────────────

def detect_deadline_cascade(student_id: str, window_days: int = 7) -> dict:
    upcoming = get_upcoming_deadlines(student_id, days=window_days)
    if len(upcoming) < 3:
        return {
            "cascade": False, "count": len(upcoming),
            "items": upcoming, "alert": None,
            "priority_order": [], "suggestion": None
        }

    def urgency_rank(d: Deadline) -> int:
        u = classify_urgency(d)
        return {"critical": 0, "high": 1, "medium": 2, "low": 3}[u]

    sorted_deadlines = sorted(upcoming, key=urgency_rank)
    priority_lines = []
    for i, d in enumerate(sorted_deadlines, 1):
        urgency = classify_urgency(d)
        emoji = urgency_emoji(urgency)
        priority_lines.append(
            f"  {i}. {emoji} {d.title} "
            f"({d.type}) — due {d.due_date.strftime('%b %d, %I:%M %p')}"
        )

    alert = (
        f"⚠️ Deadline collision detected! "
        f"You have {len(upcoming)} things due in {window_days} days."
    )
    suggestion = "Here's the priority order I'd suggest:\n" + "\n".join(priority_lines)

    return {
        "cascade": True, "count": len(upcoming),
        "items": sorted_deadlines, "alert": alert,
        "priority_order": priority_lines, "suggestion": suggestion
    }


# ─────────────────────────────────────────────
# EVENT + DEADLINE COLLISION CHECKER
# ─────────────────────────────────────────────

def check_event_deadline_collision(student_id: str) -> list[str]:
    profile = get_student_profile(student_id)
    if not profile:
        return []

    deadlines = get_upcoming_deadlines(student_id, days=7)
    deadline_days = {d.due_date.strftime("%Y-%m-%d"): d for d in deadlines}

    all_events = get_all_events()
    registered_events = [e for e in all_events if e.event_id in profile.registered_events]

    warnings = []
    for event in registered_events:
        event_day = event.event_datetime.strftime("%Y-%m-%d")
        if event_day in deadline_days:
            clashing_deadline = deadline_days[event_day]
            warnings.append(
                f"⚡ '{event.name}' and '{clashing_deadline.title}' "
                f"are both on {event.event_datetime.strftime('%b %d')} — "
                f"plan your time carefully."
            )
    return warnings


# ─────────────────────────────────────────────
# CLUB EVENT REMINDER
# ─────────────────────────────────────────────

def get_club_event_reminders(student_id: str) -> list[str]:
    profile = get_student_profile(student_id)
    if not profile:
        return []

    clubs = get_student_clubs(student_id)
    all_events = get_all_events()
    now = datetime.now()
    cutoff = now + timedelta(hours=48)

    reminders = []
    for club in clubs:
        for event_id in club.upcoming_events:
            event = next((e for e in all_events if e.event_id == event_id), None)
            if not event:
                continue
            if now <= event.event_datetime <= cutoff:
                if event.event_id not in profile.registered_events:
                    reminders.append(
                        f"📌 Your club '{club.name}' has '{event.name}' "
                        f"at {event.event_datetime.strftime('%I:%M %p')} "
                        f"— you haven't registered yet."
                    )
    return reminders


# ─────────────────────────────────────────────
# MASTER REMINDER ENGINE
# ─────────────────────────────────────────────

def get_smart_reminders(student_id: str) -> dict:
    profile = get_student_profile(student_id)
    if not profile:
        return {}

    patterns = get_attendance_patterns(student_id)

    upcoming = get_upcoming_deadlines(student_id, days=7)
    urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    upcoming_sorted = sorted(upcoming, key=lambda d: urgency_order[classify_urgency(d)])
    deadline_reminders = [
        generate_reminder_message(d, classify_urgency(d), patterns)
        for d in upcoming_sorted
    ]

    cascade = detect_deadline_cascade(student_id, window_days=7)
    collisions = check_event_deadline_collision(student_id)
    club_reminders = get_club_event_reminders(student_id)

    total = len(deadline_reminders) + len(club_reminders)
    if cascade["cascade"]:
        summary = (
            f"🚨 Cascade alert: {cascade['count']} deadlines "
            f"colliding this week. Needs prioritization help."
        )
    elif total == 0:
        summary = "✅ Nothing urgent this week."
    elif total == 1:
        summary = deadline_reminders[0] if deadline_reminders else club_reminders[0]
    else:
        summary = (
            f"You have {len(deadline_reminders)} deadline(s) "
            f"and {len(club_reminders)} club event(s) coming up."
        )

    return {
        "deadline_reminders": deadline_reminders,
        "cascade": cascade,
        "collision_warnings": collisions,
        "club_reminders": club_reminders,
        "summary": summary,
        "patterns": patterns
    }
