# backend/api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from backend.agent import run_agent
from backend.recommender import (
    get_recommendations,
    get_fresher_recommendations,
    get_avoidance_flags
)
from backend.filters import (
    apply_all_filters,
    detect_interest_drift,
    get_exam_pressure_level
)
from backend.reminders import (
    get_smart_reminders,
    detect_deadline_cascade
)
from backend.social import (
    get_social_nudges,
    run_contrast_demo
)
from backend.database import (
    get_student_profile,
    get_all_events,
    get_upcoming_deadlines,
    get_all_students,
    is_fresher
)


# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────

app = FastAPI(
    title="Smart Campus AI Assistant",
    description="AI-powered campus assistant with Hindsight memory",
    version="1.0.0"
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# REQUEST BODIES
# ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    student_id: str
    message: str = ""          # empty = proactive mode


class RetainRequest(BaseModel):
    student_id: str
    content: str

class AskRequest(BaseModel):
    question: str
    student_id: str = "student-001"  # default


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status": "running",
        "app": "Smart Campus AI Assistant",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ─────────────────────────────────────────────
# STUDENT ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/profile/{student_id}")
async def get_profile(student_id: str):
    """
    Returns student profile.
    Used by frontend to show student info.
    """
    profile = get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "student_id": profile.student_id,
        "name": profile.name,
        "year": profile.year,
        "interests": profile.interests,
        "enrolled_clubs": profile.enrolled_clubs,
        "is_fresher": is_fresher(student_id),
        "exam_pressure": get_exam_pressure_level(student_id)
    }


@app.get("/students")
async def list_students():
    """
    Returns all students.
    Used for demo/testing purposes.
    """
    students = get_all_students()
    return [
        {
            "student_id": s.student_id,
            "name": s.name,
            "year": s.year,
            "interests": s.interests,
            "is_fresher": is_fresher(s.student_id)
        }
        for s in students
    ]


# ─────────────────────────────────────────────
# CHAT ENDPOINT
# Core agent interaction
# ─────────────────────────────────────────────

@app.post("/ask")
async def ask(request: AskRequest):
    """
    Alias for /chat — keeps compatibility
    with frontend calling /ask
    """
    profile = get_student_profile(request.student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    response = run_agent(request.student_id, request.question)
    return {
        "answer": response.message,
        "student_id": request.student_id,
        "timestamp": response.timestamp.isoformat()
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Empty message → proactive mode.
    Message present → respond to query.
    """
    profile = get_student_profile(request.student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    response = run_agent(request.student_id, request.message)

    return {
        "student_id": request.student_id,
        "student_name": profile.name,
        "message": response.message,
        "proactive": response.proactive,
        "timestamp": response.timestamp.isoformat()
    }


# ─────────────────────────────────────────────
# RECOMMENDATION ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/recommendations/{student_id}")
async def recommendations(student_id: str, top_n: int = 5):
    """
    Returns filtered, ranked event recommendations.
    Applies all filters automatically.
    """
    profile = get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    # Fresher mode
    if is_fresher(student_id):
        days_since_join = (datetime.now() - profile.join_date).days
        recs = get_fresher_recommendations(student_id, day_number=days_since_join)
        return {
            "student_id": student_id,
            "mode": "fresher",
            "day_number": days_since_join,
            "recommendations": [
                {
                    "event_id": r.event.event_id,
                    "event_name": r.event.name,
                    "category": r.event.category,
                    "score": r.score,
                    "reason": r.reason,
                    "cross_interest": r.cross_interest,
                    "datetime": r.event.event_datetime.isoformat(),
                    "location": r.event.location
                }
                for r in recs
            ]
        }

    # Normal mode
    avoidance = get_avoidance_flags(student_id)
    avoid_morning = avoidance.get("avoid_morning", False)

    recs = get_recommendations(student_id, top_n=top_n + 3)
    filtered, meta = apply_all_filters(recs, student_id, avoid_morning)

    return {
        "student_id": student_id,
        "mode": "normal",
        "exam_pressure": meta["exam_pressure"],
        "filters_applied": meta["filters_applied"],
        "overload_warning": meta.get("overload_warning"),
        "recommendations": [
            {
                "event_id": r.event.event_id,
                "event_name": r.event.name,
                "category": r.event.category,
                "score": r.score,
                "reason": r.reason,
                "cross_interest": r.cross_interest,
                "datetime": r.event.event_datetime.isoformat(),
                "location": r.event.location,
                "duration_minutes": r.event.duration_minutes
            }
            for r in filtered[:top_n]
        ]
    }


# ─────────────────────────────────────────────
# REMINDER ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/reminders/{student_id}")
async def reminders(student_id: str):
    """
    Returns all smart reminders for a student.
    Includes cascade detection + collision warnings.
    """
    if not get_student_profile(student_id):
        raise HTTPException(status_code=404, detail="Student not found")

    result = get_smart_reminders(student_id)

    return {
        "student_id": student_id,
        "summary": result.get("summary"),
        "deadline_reminders": result.get("deadline_reminders", []),
        "club_reminders": result.get("club_reminders", []),
        "collision_warnings": result.get("collision_warnings", []),
        "cascade": {
            "detected": result["cascade"]["cascade"],
            "count": result["cascade"]["count"],
            "alert": result["cascade"]["alert"],
            "priority_order": result["cascade"]["priority_order"],
            "suggestion": result["cascade"]["suggestion"]
        }
    }


@app.get("/deadlines/{student_id}")
async def deadlines(student_id: str, days: int = 7):
    """
    Returns upcoming deadlines for a student.
    """
    if not get_student_profile(student_id):
        raise HTTPException(status_code=404, detail="Student not found")

    upcoming = get_upcoming_deadlines(student_id, days=days)
    cascade = detect_deadline_cascade(student_id, window_days=days)

    return {
        "student_id": student_id,
        "window_days": days,
        "cascade_alert": cascade["alert"],
        "deadlines": [
            {
                "deadline_id": d.deadline_id,
                "title": d.title,
                "type": d.type,
                "due_date": d.due_date.isoformat(),
                "is_completed": d.is_completed
            }
            for d in upcoming
        ]
    }


# ─────────────────────────────────────────────
# MEMORY ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/retain")
async def retain_memory(request: RetainRequest):
    """
    Manually store a memory for a student.
    Used by frontend for explicit interactions.
    """
    from backend.agent import _retain
    if not get_student_profile(request.student_id):
        raise HTTPException(status_code=404, detail="Student not found")

    _retain(request.student_id, request.content)

    return {
        "status": "stored",
        "student_id": request.student_id,
        "content": request.content,
        "timestamp": datetime.now().isoformat()
    }


# ─────────────────────────────────────────────
# INSIGHT ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/drift/{student_id}")
async def interest_drift(student_id: str):
    """
    Returns interest drift analysis for a student.
    Shows emerging and fading interests.
    """
    if not get_student_profile(student_id):
        raise HTTPException(status_code=404, detail="Student not found")

    drift = detect_interest_drift(student_id)

    return {
        "student_id": student_id,
        "drift_detected": drift["drift_detected"],
        "emerging": drift["emerging"],
        "fading": drift["fading"],
        "stable": drift["stable"]
    }


@app.get("/avoidance/{student_id}")
async def avoidance_flags(student_id: str):
    """
    Returns what the student silently avoids.
    Based purely on behavioral memory.
    """
    if not get_student_profile(student_id):
        raise HTTPException(status_code=404, detail="Student not found")

    flags = get_avoidance_flags(student_id)

    return {
        "student_id": student_id,
        "avoided_categories": flags.get("avoided_categories", []),
        "avoid_morning": flags.get("avoid_morning", False),
        "avoid_long_events": flags.get("avoid_long_events", False)
    }


# ─────────────────────────────────────────────
# SOCIAL ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/nudges/{student_id}")
async def social_nudges(student_id: str):
    """
    Returns social graph nudges for a student.
    Privacy-safe — never exposes other student data.
    """
    if not get_student_profile(student_id):
        raise HTTPException(status_code=404, detail="Student not found")

    nudges = get_social_nudges(student_id)

    return {
        "student_id": student_id,
        "summary": nudges["summary"],
        "nudges": nudges["nudges"],
        "overlap_count": nudges["overlap_count"],
        "top_shared_interests": nudges["top_shared_interests"]
    }


# ─────────────────────────────────────────────
# DEMO ENDPOINT
# Judge showstopper
# ─────────────────────────────────────────────

@app.get("/demo/contrast")
async def contrast_demo():
    """
    Two-student contrast demo.
    Same query → completely different outputs.
    This is your judge moment.
    """
    results = run_contrast_demo()

    return {
        "query": "What should I do this evening?",
        "description": (
            "Same campus, same events, same query — "
            "completely different recommendations "
            "based purely on Hindsight memory."
        ),
        "students": results
    }


@app.get("/demo/events")
async def all_events():
    """
    Returns all campus events.
    Used for demo and frontend display.
    """
    events = get_all_events()
    return {
        "total": len(events),
        "events": [
            {
                "event_id": e.event_id,
                "name": e.name,
                "category": e.category,
                "datetime": e.event_datetime.isoformat(),
                "location": e.location,
                "attendees_count": len(e.attendees),
                "is_morning": e.is_morning,
                "duration_minutes": e.duration_minutes
            }
            for e in events
        ]
    }
