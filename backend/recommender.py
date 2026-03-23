# backend/recommender.py

from datetime import datetime
from backend.models import Recommendation, Event
from backend.database import (
    get_all_events,
    get_student_profile,
    get_student_clubs,
    is_fresher
)
# FIX: import _recall from memory.recall — NOT from backend.agent (circular import)
from memory.recall import _recall
from backend.llm import call_llm_structured


# ─────────────────────────────────────────────
# INTEREST SCORING
# ─────────────────────────────────────────────

CATEGORY_WEIGHTS = {
    "tech": 1.0,
    "entrepreneurship": 1.0,
    "arts": 1.0,
    "sports": 1.0,
    "cultural": 1.0,
}


def score_event_for_student(
    event: Event,
    student_interests: list[str],
    avoided_categories: list[str],
    avoid_morning: bool
) -> float:
    score = 0.0
    if event.category in avoided_categories:
        return 0.0
    if avoid_morning and event.is_morning:
        return 0.0
    if event.category in student_interests:
        score += 0.6
    adjacent = {
        "tech": ["entrepreneurship"],
        "entrepreneurship": ["tech", "cultural"],
        "arts": ["cultural"],
        "cultural": ["arts"],
        "sports": []
    }
    for interest in student_interests:
        if event.category in adjacent.get(interest, []):
            score += 0.2
            break
    days_away = (event.event_datetime - datetime.now()).days
    if days_away < 0:
        return 0.0
    elif days_away <= 1:
        score += 0.2
    elif days_away <= 3:
        score += 0.1
    return min(score, 1.0)


# ─────────────────────────────────────────────
# AVOIDANCE FLAG EXTRACTOR
# ─────────────────────────────────────────────

def get_avoidance_flags(student_id: str) -> dict:
    from memory.avoidance import detect_avoidance_from_memory
    return detect_avoidance_from_memory(student_id)


# ─────────────────────────────────────────────
# CROSS INTEREST DETECTOR
# ─────────────────────────────────────────────

def detect_cross_interest(
    event: Event,
    student_interests: list[str]
) -> tuple[bool, str]:
    bridges = {
        ("tech", "entrepreneurship"): [
            "startup-pitch-01", "founders-talk-01", "hackathon-01"
        ],
        ("arts", "cultural"): [
            "open-mic-01", "drama-rehearsal-01", "debate-01"
        ],
        ("tech", "arts"): [
            "photography-walk-01"
        ],
    }
    for (cat1, cat2), event_ids in bridges.items():
        if (
            cat1 in student_interests and
            cat2 in student_interests and
            event.event_id in event_ids
        ):
            return True, f"Bridges your interest in {cat1} and {cat2}"
    return False, ""


# ─────────────────────────────────────────────
# CLUB MEMBER ATTENDING BONUS
# ─────────────────────────────────────────────

def club_member_bonus(
    event: Event,
    student_id: str
) -> tuple[float, str]:
    clubs = get_student_clubs(student_id)
    attending_clubs = []
    for club in clubs:
        members = set(club.members) - {student_id}
        attending = members.intersection(set(event.attendees))
        if attending:
            attending_clubs.append(club.name)
    if attending_clubs:
        return 0.15, f"{', '.join(attending_clubs)} members are attending"
    return 0.0, ""


# ─────────────────────────────────────────────
# MAIN RECOMMENDATION ENGINE
# ─────────────────────────────────────────────

def get_recommendations(student_id: str, top_n: int = 5) -> list[Recommendation]:
    profile = get_student_profile(student_id)
    if not profile:
        return []

    avoidance = get_avoidance_flags(student_id)
    avoided_categories = avoidance.get("avoided_categories", [])
    avoid_morning = avoidance.get("avoid_morning", False)
    avoid_long = avoidance.get("avoid_long_events", False)

    all_events = get_all_events()
    scored = []

    for event in all_events:
        if event.event_id in profile.registered_events:
            continue
        if avoid_long and event.duration_minutes > 180:
            continue

        base_score = score_event_for_student(
            event, profile.interests, avoided_categories, avoid_morning
        )
        if base_score == 0.0:
            continue

        is_cross, cross_reason = detect_cross_interest(event, profile.interests)
        cross_bonus = 0.1 if is_cross else 0.0
        member_bonus, member_reason = club_member_bonus(event, student_id)

        final_score = min(base_score + cross_bonus + member_bonus, 1.0)

        reasons = []
        if event.category in profile.interests:
            reasons.append(f"Matches your interest in {event.category}")
        if is_cross:
            reasons.append(cross_reason)
        if member_reason:
            reasons.append(member_reason)
        reason = " · ".join(reasons) if reasons else "Relevant to your profile"

        scored.append(
            Recommendation(
                event=event,
                score=round(final_score, 2),
                reason=reason,
                cross_interest=is_cross
            )
        )

    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:top_n]


# ─────────────────────────────────────────────
# FRESHER RECOMMENDATION
# ─────────────────────────────────────────────

def get_fresher_recommendations(
    student_id: str,
    day_number: int
) -> list[Recommendation]:
    if day_number <= 7:
        focus_categories = ["tech", "arts", "cultural"]
    elif day_number <= 14:
        focus_categories = ["entrepreneurship", "sports"]
    elif day_number <= 21:
        focus_categories = ["cultural", "arts"]
    else:
        return get_recommendations(student_id, top_n=3)

    all_events = get_all_events()
    fresher_picks = []
    for event in all_events:
        if event.category in focus_categories:
            fresher_picks.append(
                Recommendation(
                    event=event,
                    score=0.8,
                    reason=f"Great for exploring {event.category} in your first month",
                    cross_interest=False
                )
            )
    return fresher_picks[:2]
