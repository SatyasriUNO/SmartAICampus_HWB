# memory/cross_interest.py

from memory.recall import get_interest_memory
from backend.llm import call_llm_structured


# ─────────────────────────────────────────────
# INTEREST EXTRACTOR
# Pulls top interest categories from memory
# ─────────────────────────────────────────────

def extract_top_interests(student_id: str) -> list[str]:
    """
    Reads memory and extracts top interest categories.
    Returns ranked list of categories.
    """
    memory = get_interest_memory(student_id)

    prompt = f"""
Analyze this student's memory and identify their top interest categories.

Memory:
{memory}

Return ONLY a JSON array of categories, ranked by strength.
Choose from: tech, arts, sports, cultural, entrepreneurship

Example: ["tech", "entrepreneurship", "arts"]

If memory is empty return: []
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
# CROSS INTEREST OPPORTUNITY FINDER
# Connects dots across multiple interests
# ─────────────────────────────────────────────

def find_cross_interest_opportunities(
    student_id: str,
    available_events: list[dict]
) -> list[dict]:
    """
    Takes student memory + available events and
    surfaces opportunities that bridge 2+ interests.

    available_events format:
    [{"name": str, "category": str, "event_id": str}]

    Returns ranked list of opportunities with reasons.
    """
    top_interests = extract_top_interests(student_id)
    memory = get_interest_memory(student_id)

    if not top_interests or len(top_interests) < 2:
        return []

    events_str = "\n".join(
        f"- {e['name']} (category: {e['category']}, id: {e['event_id']})"
        for e in available_events
    )

    prompt = f"""
You are finding hidden opportunities for a student by connecting their interests.

Student's top interests: {top_interests}

Student's memory context:
{memory}

Available events:
{events_str}

Find events that connect TWO OR MORE of the student's interests.
These are events the student wouldn't think to search for
but would genuinely benefit from.

Return ONLY a JSON array:
[
  {{
    "event_id": "...",
    "event_name": "...",
    "connection": "Bridges your interest in X and Y",
    "score": 0.9
  }}
]

Rules:
- Only include genuine cross-interest connections
- Score 0.0 to 1.0 based on how strong the connection is
- Maximum 3 results
- If no genuine connections exist return []
Return ONLY the JSON array. No explanation.
"""

    try:
        import json
        raw = call_llm_structured(prompt)
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        results = json.loads(clean)
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    except Exception:
        return []


# ─────────────────────────────────────────────
# UNDERLYING PATTERN DETECTOR
# Finds the hidden career/life pattern
# ─────────────────────────────────────────────

def detect_underlying_pattern(student_id: str) -> str:
    """
    Looks across all interests and detects the
    underlying pattern driving student behavior.

    Example:
    coding + entrepreneurship + internships
    → "career-focused tech growth"
    """
    memory = get_interest_memory(student_id)

    prompt = f"""
Look at this student's activity memory and identify
the single underlying pattern or goal driving their behavior.

Memory:
{memory}

Return ONLY one short phrase (5-8 words) describing
the underlying pattern.

Examples:
- "career-focused tech and entrepreneurship growth"
- "creative arts and social expression seeker"
- "competitive sports and fitness achiever"

If memory is empty return: "still exploring interests"
Return ONLY the phrase. No explanation.
"""

    try:
        raw = call_llm_structured(prompt)
        return raw.strip().strip('"').strip("'")
    except Exception:
        return "still exploring interests"
