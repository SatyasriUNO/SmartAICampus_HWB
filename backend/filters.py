# backend/filters.py

from datetime import datetime, timedelta
from backend.models import Recommendation
from backend.database import (
    get_upcoming_deadlines,
    get_student_profile,
    is_fresher
)
# FIX: import _recall from memory.recall — NOT from backend.agent (circular import)
from memory.recall import _recall
from backend.llm import call_llm_structured


# ─────────────────────────────────────────────
# EXAM / DEADLINE WEEK DETECTOR
# ─────────────────────────────────────────────

def is_exam_week(student_id: str, threshold_days: int = 5) -> bool:
    deadlines = get_upcoming_deadlines(student_id, days=threshold_days)
    academic = [d for d in deadlines if d.type == "academic"]
    return len(academic) > 0


def get_exam_pressure_level(student_id: str) -> str:
    deadlines_3 = get_upcoming_deadlines(student_id, days=3)
    deadlines_5 = get_upcoming_deadlines(student_id, days=5)
    academic_3 = [d for d in deadlines_3 if d.type == "academic"]
    academic_5 = [d for d in deadlines_5 if d.type == "academic"]
    if len(academic_3) >= 1:
        return "high"
    elif len(academic_5) >= 1:
        return "medium"
    else:
        return "low"


# ─────────────────────────────────────────────
# TIME OF DAY FILTER
# ─────────────────────────────────────────────

def filter_by_time_preference(
    recommendations: list[Recommendation],
    avoid_morning: bool
) -> list[Recommendation]:
    if not avoid_morning:
        return recommendations
    filtered = [r for r in recommendations if not r.event.is_morning]
    removed = len(recommendations) - len(filtered)
    if removed > 0:
        print(f"  [filter] Removed {removed} morning event(s) based on preference")
    return filtered


# ─────────────────────────────────────────────
# EXAM WEEK FILTER
# ─────────────────────────────────────────────

def filter_by_exam_pressure(
    recommendations: list[Recommendation],
    student_id: str
) -> list[Recommendation]:
    pressure = get_exam_pressure_level(student_id)
    if pressure == "high":
        print(f"  [filter] Exam pressure HIGH — limiting to 2 light suggestions")
        light = [r for r in recommendations if r.event.duration_minutes <= 90]
        return light[:2]
    elif pressure == "medium":
        print(f"  [filter] Exam pressure MEDIUM — limiting to 3 suggestions")
        return recommendations[:3]
    return recommendations


# ─────────────────────────────────────────────
# OVERLOAD FILTER
# ─────────────────────────────────────────────

def filter_by_day_overload(
    recommendations: list[Recommendation],
    student_id: str
) -> tuple[list[Recommendation], str | None]:
    profile = get_student_profile(student_id)
    if not profile:
        return recommendations, None

    day_load: dict[str, int] = {}
    all_deadlines = get_upcoming_deadlines(student_id, days=7)
    for d in all_deadlines:
        day_key = d.due_date.strftime("%Y-%m-%d")
        day_load[day_key] = day_load.get(day_key, 0) + 1

    for r in recommendations:
        day_key = r.event.event_datetime.strftime("%Y-%m-%d")
        day_load[day_key] = day_load.get(day_key, 0) + 1

    overloaded_days = [day for day, count in day_load.items() if count >= 3]

    warning = None
    if overloaded_days:
        days_str = ", ".join(
            datetime.strptime(d, "%Y-%m-%d").strftime("%b %d")
            for d in overloaded_days
        )
        warning = (
            f"⚠️ Heads up — {days_str} looks very packed. "
            f"You have deadlines and events colliding. Want help prioritizing?"
        )
        print(f"  [filter] Overload detected on: {days_str}")
        filtered = [
            r for r in recommendations
            if r.event.event_datetime.strftime("%Y-%m-%d") not in overloaded_days
            or r.cross_interest
        ]
        return filtered, warning

    return recommendations, warning


# ─────────────────────────────────────────────
# CATEGORY REPETITION FILTER
# ─────────────────────────────────────────────

def filter_category_repetition(
    recommendations: list[Recommendation]
) -> list[Recommendation]:
    category_count: dict[str, int] = {}
    filtered = []
    for r in recommendations:
        cat = r.event.category
        count = category_count.get(cat, 0)
        if count < 2:
            filtered.append(r)
            category_count[cat] = count + 1
        else:
            print(f"  [filter] Skipping {r.event.name} — too many {cat} events")
    return filtered


# ─────────────────────────────────────────────
# INTEREST DRIFT DETECTOR
# ─────────────────────────────────────────────

def detect_interest_drift(student_id: str) -> dict:
    from memory.drift import detect_interest_drift_from_memory
    return detect_interest_drift_from_memory(student_id)


# ─────────────────────────────────────────────
# DRIFT-BASED RECOMMENDATION BOOST
# ─────────────────────────────────────────────

def apply_drift_boost(
    recommendations: list[Recommendation],
    drift: dict
) -> list[Recommendation]:
    emerging = drift.get("emerging", [])
    fading = drift.get("fading", [])
    if not emerging and not fading:
        return recommendations

    boosted = []
    for r in recommendations:
        score = r.score
        reason = r.reason
        if r.event.category in emerging:
            score = min(score + 0.15, 1.0)
            reason += f" · Your interest in {r.event.category} is growing"
            print(f"  [drift] Boosted {r.event.name} — emerging interest")
        elif r.event.category in fading:
            score = max(score - 0.2, 0.0)
            print(f"  [drift] Reduced {r.event.name} — fading interest")
        boosted.append(
            Recommendation(
                event=r.event,
                score=round(score, 2),
                reason=reason,
                cross_interest=r.cross_interest
            )
        )
    boosted.sort(key=lambda r: r.score, reverse=True)
    return boosted


# ─────────────────────────────────────────────
# MASTER FILTER PIPELINE
# ─────────────────────────────────────────────

def apply_all_filters(
    recommendations: list[Recommendation],
    student_id: str,
    avoid_morning: bool = False
) -> tuple[list[Recommendation], dict]:
    print(f"\n  [pipeline] Starting filter pipeline for {student_id}")
    print(f"  [pipeline] Input: {len(recommendations)} recommendations")

    metadata = {
        "exam_pressure": get_exam_pressure_level(student_id),
        "is_exam_week": is_exam_week(student_id),
        "overload_warning": None,
        "drift": {},
        "filters_applied": []
    }

    if avoid_morning:
        recommendations = filter_by_time_preference(recommendations, avoid_morning)
        metadata["filters_applied"].append("morning_filter")

    if is_exam_week(student_id):
        recommendations = filter_by_exam_pressure(recommendations, student_id)
        metadata["filters_applied"].append("exam_filter")

    recommendations, overload_warning = filter_by_day_overload(recommendations, student_id)
    if overload_warning:
        metadata["overload_warning"] = overload_warning
        metadata["filters_applied"].append("overload_filter")

    recommendations = filter_category_repetition(recommendations)
    metadata["filters_applied"].append("diversity_filter")

    drift = detect_interest_drift(student_id)
    if drift.get("drift_detected"):
        recommendations = apply_drift_boost(recommendations, drift)
        metadata["drift"] = drift
        metadata["filters_applied"].append("drift_boost")

    print(f"  [pipeline] Output: {len(recommendations)} recommendations")
    print(f"  [pipeline] Filters applied: {metadata['filters_applied']}")

    return recommendations, metadata
