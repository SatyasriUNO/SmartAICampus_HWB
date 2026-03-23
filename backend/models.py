# backend/models.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────────
# STUDENT
# ─────────────────────────────────────────────

class StudentProfile(BaseModel):
    student_id: str
    name: str
    year: int                        # 1 = fresher, 2/3/4 = senior
    enrolled_clubs: list[str]        # list of club_ids
    registered_events: list[str]     # list of event_ids
    academic_deadlines: list[str]    # list of deadline_ids
    join_date: datetime              # used to detect fresher mode
    interests: list[str]             # inferred tags: ["tech", "entrepreneurship"]


# ─────────────────────────────────────────────
# EVENT
# ─────────────────────────────────────────────

class Event(BaseModel):
    event_id: str
    name: str
    category: str                    # tech, arts, sports, entrepreneurship, cultural
    event_datetime: datetime
    location: str
    attendees: list[str]             # student_ids who registered
    duration_minutes: int
    is_morning: bool                 # True if before 12PM


# ─────────────────────────────────────────────
# CLUB
# ─────────────────────────────────────────────

class Club(BaseModel):
    club_id: str
    name: str
    category: str                    # tech, arts, sports, entrepreneurship, cultural
    members: list[str]               # student_ids
    upcoming_events: list[str]       # event_ids run by this club


# ─────────────────────────────────────────────
# DEADLINE
# ─────────────────────────────────────────────

class Deadline(BaseModel):
    deadline_id: str
    title: str
    type: str                        # academic, club, fest, internship
    due_date: datetime
    student_id: str                  # who this deadline belongs to
    is_completed: bool = False


# ─────────────────────────────────────────────
# CAMPUS SPACE
# ─────────────────────────────────────────────

class CampusSpace(BaseModel):
    space_id: str
    name: str                        # "Block C Seminar Hall", "Amphitheatre"
    location_tag: str                # for map integration later (Gouri's part)
    capacity: int


# ─────────────────────────────────────────────
# MEMORY ENTRY (shared schema with memory/ layer)
# ─────────────────────────────────────────────

class MemoryEntry(BaseModel):
    student_id: str
    action: str                      # attended, ignored, joined, dropped, queried
    target_type: str                 # event, club, deadline, space
    target_name: str
    category: str                    # tech, arts, sports, entrepreneurship, cultural
    timestamp: datetime
    time_of_day: str                 # morning, afternoon, evening, night
    metadata: Optional[dict] = {}   # any extra context


# ─────────────────────────────────────────────
# RECOMMENDATION OUTPUT
# ─────────────────────────────────────────────

class Recommendation(BaseModel):
    event: Event
    score: float                     # 0.0 to 1.0
    reason: str                      # human readable explanation
    cross_interest: bool = False     # True if connects 2+ interest areas


# ─────────────────────────────────────────────
# AGENT RESPONSE
# ─────────────────────────────────────────────

class AgentResponse(BaseModel):
    student_id: str
    message: str                     # the response text
    recommendations: list[Recommendation] = []
    reminders: list[str] = []
    proactive: bool = False          # True if agent spoke without being asked
    timestamp: datetime = datetime.now()


# ─────────────────────────────────────────────
# HELPER: detect time of day
# ─────────────────────────────────────────────

def get_time_of_day(dt: datetime) -> str:
    hour = dt.hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"
