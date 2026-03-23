# memory/avoidance.py — REPLACE ENTIRE FILE WITH THIS

from memory.recall import get_avoidance_memory
from backend.llm import call_llm_structured


def detect_avoidance_from_memory(student_id: str) -> dict:
    """
    Reads Hindsight memory and detects
    what the student consistently avoids.
    Returns structured avoidance flags.
    """
    memory = get_avoidance_memory(student_id)

    prompt = f"""
Analyze this student's memory for avoidance patterns.

Memory:
{memory}

Return ONLY a JSON object:
{{
  "avoided_categories": [],
  "avoid_morning": false,
  "avoid_long_events": false
}}

Rules:
- avoided_categories: categories student consistently ignores
  (choose from: tech, arts, sports, cultural, entrepreneurship)
- avoid_morning: true if student repeatedly ignores morning events
- avoid_long_events: true if student avoids events over 3 hours
- If memory empty return all defaults
Return ONLY the JSON. No explanation.
"""

    try:
        import json
        raw = call_llm_structured(prompt)
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {
            "avoided_categories": [],
            "avoid_morning": False,
            "avoid_long_events": False
        }


def detect_avoidance(interaction_history: list) -> list:
    """
    Bikash's original function — kept for compatibility.
    Works on raw interaction list passed directly.
    """
    category_ignore_count = {}
    for interaction in interaction_history:
        if interaction.get("action") == "ignored":
            cat = interaction.get("category")
            category_ignore_count[cat] = category_ignore_count.get(cat, 0) + 1
    return [
        category for category, count
        in category_ignore_count.items()
        if count >= 3
    ]
