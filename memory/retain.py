# memory/retain.py

import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
from memory.schema import MemoryEntry

load_dotenv()

# ─────────────────────────────────────────────
# Hindsight client — single instance
# ─────────────────────────────────────────────

def _get_client():
    return Hindsight(
        base_url=os.getenv("HINDSIGHT_BASE_URL"),
        api_key=os.getenv("HINDSIGHT_API_KEY")
    )

# ─────────────────────────────────────────────
# CORE RETAIN
# ─────────────────────────────────────────────

def retain(student_id: str, content: str) -> bool:
    try:
        client = _get_client()
        client.retain(bank_id=student_id, content=content)
        print(f"  [retain] ✅ Stored for {student_id}: {content[:60]}...")
        return True
    except Exception as e:
        print(f"  [retain] ❌ Failed for {student_id}: {e}")
        return False


# ─────────────────────────────────────────────
# TYPED RETAIN CALLS
# One function per memory type
# ─────────────────────────────────────────────

def store_event_attended(
    student_id: str,
    event_name: str,
    category: str,
    time_of_day: str,
    location: str = ""
) -> bool:
    """
    Student attended an event.
    """
    content = (
        f"Student attended event: '{event_name}'. "
        f"Category: {category}. "
        f"Time: {time_of_day}. "
        f"Location: {location}."
    )
    return retain(student_id, content)


def store_event_ignored(
    student_id: str,
    event_name: str,
    category: str,
    time_of_day: str
) -> bool:
    """
    Student was shown an event but ignored it.
    """
    content = (
        f"Student ignored/skipped event: '{event_name}'. "
        f"Category: {category}. "
        f"Time of day when ignored: {time_of_day}. "
        f"This suggests possible disinterest in {category} "
        f"or {time_of_day} events."
    )
    return retain(student_id, content)


def store_club_joined(
    student_id: str,
    club_name: str,
    category: str
) -> bool:
    """
    Student joined a club.
    """
    content = (
        f"Student joined club: '{club_name}'. "
        f"Category: {category}. "
        f"This indicates strong interest in {category}."
    )
    return retain(student_id, content)


def store_club_dropped(
    student_id: str,
    club_name: str,
    category: str
) -> bool:
    """
    Student dropped or stopped attending a club.
    """
    content = (
        f"Student dropped/left club: '{club_name}'. "
        f"Category: {category}. "
        f"Suggests fading interest in {category} "
        f"or this specific club format."
    )
    return retain(student_id, content)


def store_query_made(
    student_id: str,
    query: str,
    category: str = ""
) -> bool:
    """
    Student asked the assistant something.
    """
    content = (
        f"Student queried: '{query}'. "
        + (f"Related category: {category}." if category else "")
    )
    return retain(student_id, content)


def store_deadline_completed(
    student_id: str,
    deadline_title: str,
    deadline_type: str,
    completed_on_time: bool
) -> bool:
    """
    Student completed a deadline.
    """
    timing = "on time" if completed_on_time else "late"
    content = (
        f"Student completed deadline: '{deadline_title}'. "
        f"Type: {deadline_type}. "
        f"Completed: {timing}."
    )
    return retain(student_id, content)


def store_deadline_missed(
    student_id: str,
    deadline_title: str,
    deadline_type: str
) -> bool:
    """
    Student missed a deadline.
    """
    content = (
        f"Student missed deadline: '{deadline_title}'. "
        f"Type: {deadline_type}. "
        f"This may indicate overload or disengagement."
    )
    return retain(student_id, content)


def store_interaction(
    student_id: str,
    user_input: str,
    agent_response: str,
    time_of_day: str
) -> bool:
    """
    Stores a full conversation interaction.
    Called after every agent response.
    """
    content = (
        f"[{time_of_day}] "
        f"Student said: '{user_input[:100]}'. "
        f"Agent responded about: '{agent_response[:100]}'."
    )
    return retain(student_id, content)


def store_memory_entry(entry: MemoryEntry) -> bool:
    """
    Stores a structured MemoryEntry object.
    Converts to natural language before storing.
    """
    content = (
        f"Student {entry.action} {entry.target_type}: "
        f"'{entry.target_name}'. "
        f"Category: {entry.category}. "
        f"Time: {entry.time_of_day}. "
        f"Date: {entry.timestamp.strftime('%b %d %Y')}."
    )
    if entry.metadata:
        extras = ", ".join(f"{k}: {v}" for k, v in entry.metadata.items())
        content += f" Extra context: {extras}."

    return retain(entry.student_id, content)
