# backend/agent.py

import os
from datetime import datetime
from backend.models import AgentResponse, get_time_of_day
from backend.database import (
    get_student_profile,
    get_upcoming_deadlines,
    get_student_clubs,
    is_fresher,
    get_cascade_window,
    get_all_events
)
from backend.llm import call_llm
from memory.retain import store_interaction
from memory.recall import recall_as_string


# ─────────────────────────────────────────────
# MEMORY LAYER
# Swap these two functions when Hindsight is live
# ─────────────────────────────────────────────

_memory_store: dict[str, list[str]] = {}

def _retain(student_id: str, content: str):
    store_interaction(
        student_id=student_id,
        user_input=content,
        agent_response="",
        time_of_day=""
    )

def _recall(student_id: str, query: str) -> str:
    return recall_as_string(student_id, query)


# ─────────────────────────────────────────────
# CONTEXT BUILDER
# ─────────────────────────────────────────────

def build_context(student_id: str) -> str:
    """
    Assembles full context string for LLM.
    Pulls from database + memory layer.
    """
    profile = get_student_profile(student_id)
    if not profile:
        return "Unknown student."

    # Deadlines
    deadlines = get_upcoming_deadlines(student_id, days=7)
    deadline_str = (
        "\n".join(
            f"  • {d.title} ({d.type}) "
            f"— due {d.due_date.strftime('%b %d %I:%M %p')}"
            for d in deadlines
        )
        if deadlines else "  None this week"
    )

    # Clubs
    clubs = get_student_clubs(student_id)
    club_str = (
        ", ".join(c.name for c in clubs)
        if clubs else "None"
    )

    # Cascade
    cascade = get_cascade_window(student_id, days=7)
    cascade_str = (
        cascade["alert"]
        if cascade["alert"]
        else "No deadline collision this week"
    )

    # Fresher
    fresher_str = (
        "YES — guide gently, build habits"
        if is_fresher(student_id)
        else "No"
    )

    # Memory
    memory = _recall(
        student_id,
        "student interests habits events clubs attended ignored"
    )

    return f"""
Student: {profile.name} | Year: {profile.year} | Interests: {', '.join(profile.interests)}
Fresher Mode: {fresher_str}

Upcoming Deadlines (next 7 days):
{deadline_str}

Deadline Cascade Warning: {cascade_str}

Enrolled Clubs: {club_str}

Past Memory (from Hindsight):
{memory}
"""


# ─────────────────────────────────────────────
# PROACTIVE TRIGGER CHECK
# ─────────────────────────────────────────────

def check_proactive_triggers(student_id: str) -> str | None:
    """
    Checks for urgent triggers on session start.
    Returns message string or None.
    """
    profile = get_student_profile(student_id)
    if not profile:
        return None

    triggers = []

    # Deadline cascade
    cascade = get_cascade_window(student_id, days=5)
    if cascade["cascade"]:
        triggers.append(cascade["alert"])

    # Deadline within 48 hours
    urgent = get_upcoming_deadlines(student_id, days=2)
    for d in urgent:
        triggers.append(
            f"🔴 {d.title} is due in less than 48 hours!"
        )

    # Club event today
    clubs = get_student_clubs(student_id)
    today = datetime.now().date()
    all_events = get_all_events()
    for event in all_events:
        if event.event_datetime.date() == today:
            for club in clubs:
                if event.event_id in club.upcoming_events:
                    triggers.append(
                        f"📅 Your club '{club.name}' has "
                        f"'{event.name}' today at "
                        f"{event.event_datetime.strftime('%I:%M %p')} "
                        f"in {event.location}."
                    )

    return " | ".join(triggers) if triggers else None


# ─────────────────────────────────────────────
# FULL CONTEXT ASSEMBLER
# Wires in ALL modules for complete response
# ─────────────────────────────────────────────

def assemble_full_context(student_id: str) -> dict:
    """
    Calls every module and assembles a complete
    picture of what the agent needs to respond.
    Returns dict with all context pieces.
    """

    # Import here to avoid circular imports
    from backend.recommender import (
        get_recommendations,
        get_fresher_recommendations,
        get_avoidance_flags
    )
    from backend.filters import apply_all_filters
    from backend.reminders import get_smart_reminders
    from backend.social import get_social_nudges

    profile = get_student_profile(student_id)
    if not profile:
        return {}

    # 1. Base context
    base_context = build_context(student_id)

    # 2. Avoidance flags
    avoidance = get_avoidance_flags(student_id)
    avoid_morning = avoidance.get("avoid_morning", False)

    # 3. Recommendations
    if is_fresher(student_id):
        days_since = (datetime.now() - profile.join_date).days
        recs = get_fresher_recommendations(student_id, day_number=days_since)
    else:
        raw_recs = get_recommendations(student_id, top_n=8)
        recs, filter_meta = apply_all_filters(
            raw_recs, student_id, avoid_morning
        )
        recs = recs[:5]

    rec_str = (
        "\n".join(
            f"  • {r.event.name} ({r.event.category}) "
            f"— {r.reason}"
            + (" [CROSS-INTEREST]" if r.cross_interest else "")
            for r in recs
        )
        if recs else "  No recommendations available"
    )

    # 4. Reminders
    reminders = get_smart_reminders(student_id)
    reminder_str = reminders.get("summary", "Nothing urgent.")

    # collision warnings
    collisions = reminders.get("collision_warnings", [])
    collision_str = (
        "\n".join(f"  {w}" for w in collisions)
        if collisions else "  None"
    )

    # 5. Social nudges
    nudges = get_social_nudges(student_id)
    nudge_str = (
        "\n".join(f"  {n}" for n in nudges["nudges"])
        if nudges["nudges"] else "  None right now"
    )

    # 6. Proactive triggers
    proactive = check_proactive_triggers(student_id)
    proactive_str = proactive if proactive else "None"

    return {
        "base_context": base_context,
        "rec_str": rec_str,
        "reminder_str": reminder_str,
        "collision_str": collision_str,
        "nudge_str": nudge_str,
        "proactive_str": proactive_str,
        "avoidance": avoidance,
        "has_proactive": proactive is not None,
        "is_fresher": is_fresher(student_id),
        "recs": recs,
        "reminders": reminders,
        "nudges": nudges
    }


# ─────────────────────────────────────────────
# PROMPT BUILDER
# Builds final LLM prompt from all context
# ─────────────────────────────────────────────

def build_prompt(
    user_input: str,
    context: dict,
    student_name: str
) -> tuple[str, bool]:
    """
    Builds the final prompt for the LLM.
    Returns (prompt_string, is_proactive)
    """

    full_context = f"""
{context['base_context']}

--- TOP RECOMMENDATIONS ---
{context['rec_str']}

--- REMINDER SUMMARY ---
{context['reminder_str']}

--- EVENT + DEADLINE COLLISIONS ---
{context['collision_str']}

--- SOCIAL NUDGES ---
{context['nudge_str']}

--- PROACTIVE TRIGGERS ---
{context['proactive_str']}
"""

    is_proactive = False

    if not user_input.strip():
        # Proactive mode — agent opens conversation
        is_proactive = True
        if context["has_proactive"]:
            prompt = (
                f"Open the conversation proactively for {student_name}. "
                f"Lead with the most urgent trigger, then weave in "
                f"1-2 relevant recommendations. "
                f"Sound like a helpful senior student, not a bot. "
                f"Be specific, concise, max 3 sentences."
            )
        else:
            prompt = (
                f"Open the conversation naturally for {student_name}. "
                f"Pick the single most relevant thing from their "
                f"context and lead with that. "
                f"Max 2 sentences. Sound human."
            )
    else:
        # Responsive mode — answer what student asked
        prompt = user_input
        if context["has_proactive"]:
            prompt = (
                f"[URGENT: {context['proactive_str']}]\n\n"
                f"Student asks: {user_input}\n\n"
                f"Answer their question first, then briefly "
                f"mention the urgent alert if relevant."
            )

    return full_context, prompt, is_proactive


# ─────────────────────────────────────────────
# MAIN AGENT LOOP
# ─────────────────────────────────────────────

def run_agent(student_id: str, user_input: str = "") -> AgentResponse:
    """
    Main entry point for every student interaction.

    Flow:
    1. Assemble full context from all modules
    2. Build prompt
    3. Call LLM
    4. Retain interaction to memory
    5. Return structured response
    """

    profile = get_student_profile(student_id)
    if not profile:
        return AgentResponse(
            student_id=student_id,
            message="Student not found.",
            timestamp=datetime.now()
        )

    # Step 1: assemble everything
    context = assemble_full_context(student_id)

    # Step 2: build prompt
    full_context, prompt, is_proactive = build_prompt(
        user_input, context, profile.name
    )

    # Step 3: call LLM
    response_text = call_llm(
        user_message=prompt,
        memory_context=full_context,
        student_name=profile.name
    )

    # Step 4: retain interaction
    _retain(
        student_id,
        f"[{get_time_of_day(datetime.now())}] "
        f"Input: '{user_input[:80]}' | "
        f"Response: '{response_text[:100]}'"
    )

    # Step 5: return structured response
    return AgentResponse(
        student_id=student_id,
        message=response_text,
        recommendations=context.get("recs", []),
        reminders=context["reminders"].get("deadline_reminders", []),
        proactive=is_proactive,
        timestamp=datetime.now()
    )
