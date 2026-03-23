# backend/database.py

from datetime import datetime
from backend.models import (
    StudentProfile, Event, Club, 
    Deadline, CampusSpace
)

# ─────────────────────────────────────────────
# CAMPUS SPACES
# ─────────────────────────────────────────────

SPACES = {
    "block-c-hall": CampusSpace(
        space_id="block-c-hall",
        name="Block C Seminar Hall",
        location_tag="block_c",
        capacity=150
    ),
    "amphitheatre": CampusSpace(
        space_id="amphitheatre",
        name="Amphitheatre",
        location_tag="central_lawn",
        capacity=500
    ),
    "innovation-lab": CampusSpace(
        space_id="innovation-lab",
        name="Innovation Lab",
        location_tag="block_a",
        capacity=40
    ),
    "open-air-stage": CampusSpace(
        space_id="open-air-stage",
        name="Open Air Stage",
        location_tag="north_campus",
        capacity=300
    ),
    "sports-complex": CampusSpace(
        space_id="sports-complex",
        name="Sports Complex",
        location_tag="east_campus",
        capacity=200
    ),
}


# ─────────────────────────────────────────────
# EVENTS (mix of categories, morning + evening)
# ─────────────────────────────────────────────

EVENTS = {
    "ai-workshop-01": Event(
        event_id="ai-workshop-01",
        name="AI & ML Workshop",
        category="tech",
        event_datetime=datetime(2026, 3, 25, 18, 0),
        location="block-c-hall",
        attendees=["student-001", "student-003"],
        duration_minutes=120,
        is_morning=False
    ),
    "startup-pitch-01": Event(
        event_id="startup-pitch-01",
        name="Startup Pitch Competition",
        category="entrepreneurship",
        event_datetime=datetime(2026, 3, 26, 17, 0),
        location="innovation-lab",
        attendees=["student-002", "student-003"],
        duration_minutes=180,
        is_morning=False
    ),
    "open-mic-01": Event(
        event_id="open-mic-01",
        name="Cultural Fest Open Mic",
        category="arts",
        event_datetime=datetime(2026, 3, 25, 19, 0),
        location="amphitheatre",
        attendees=["student-002", "student-004"],
        duration_minutes=120,
        is_morning=False
    ),
    "yoga-morning-01": Event(
        event_id="yoga-morning-01",
        name="Morning Yoga Session",
        category="sports",
        event_datetime=datetime(2026, 3, 26, 6, 30),
        location="sports-complex",
        attendees=["student-004"],
        duration_minutes=60,
        is_morning=True
    ),
    "hackathon-01": Event(
        event_id="hackathon-01",
        name="24hr Campus Hackathon",
        category="tech",
        event_datetime=datetime(2026, 3, 28, 9, 0),
        location="innovation-lab",
        attendees=["student-001", "student-003"],
        duration_minutes=1440,
        is_morning=True
    ),
    "photography-walk-01": Event(
        event_id="photography-walk-01",
        name="Photography Campus Walk",
        category="arts",
        event_datetime=datetime(2026, 3, 27, 7, 0),
        location="open-air-stage",
        attendees=["student-004"],
        duration_minutes=90,
        is_morning=True
    ),
    "debate-01": Event(
        event_id="debate-01",
        name="Inter-College Debate",
        category="cultural",
        event_datetime=datetime(2026, 3, 29, 14, 0),
        location="block-c-hall",
        attendees=["student-002"],
        duration_minutes=180,
        is_morning=False
    ),
    "sports-tournament-01": Event(
        event_id="sports-tournament-01",
        name="Badminton Tournament",
        category="sports",
        event_datetime=datetime(2026, 3, 30, 8, 0),
        location="sports-complex",
        attendees=["student-004"],
        duration_minutes=240,
        is_morning=True
    ),
    "founders-talk-01": Event(
        event_id="founders-talk-01",
        name="Founders Talk: Building in College",
        category="entrepreneurship",
        event_datetime=datetime(2026, 3, 27, 18, 0),
        location="block-c-hall",
        attendees=["student-001", "student-002"],
        duration_minutes=90,
        is_morning=False
    ),
    "drama-rehearsal-01": Event(
        event_id="drama-rehearsal-01",
        name="Drama Club Rehearsal",
        category="arts",
        event_datetime=datetime(2026, 3, 26, 16, 0),
        location="open-air-stage",
        attendees=["student-004", "student-002"],
        duration_minutes=120,
        is_morning=False
    ),
}


# ─────────────────────────────────────────────
# CLUBS
# ─────────────────────────────────────────────

CLUBS = {
    "coding-society": Club(
        club_id="coding-society",
        name="Coding Society",
        category="tech",
        members=["student-001", "student-003"],
        upcoming_events=["ai-workshop-01", "hackathon-01"]
    ),
    "entrepreneurship-cell": Club(
        club_id="entrepreneurship-cell",
        name="Entrepreneurship Cell",
        category="entrepreneurship",
        members=["student-001", "student-002"],
        upcoming_events=["startup-pitch-01", "founders-talk-01"]
    ),
    "drama-club": Club(
        club_id="drama-club",
        name="Drama Club",
        category="arts",
        members=["student-002", "student-004"],
        upcoming_events=["drama-rehearsal-01", "open-mic-01"]
    ),
    "debate-society": Club(
        club_id="debate-society",
        name="Debate Society",
        category="cultural",
        members=["student-002"],
        upcoming_events=["debate-01"]
    ),
    "photography-club": Club(
        club_id="photography-club",
        name="Photography Club",
        category="arts",
        members=["student-004"],
        upcoming_events=["photography-walk-01"]
    ),
    "sports-council": Club(
        club_id="sports-council",
        name="Sports Council",
        category="sports",
        members=["student-004"],
        upcoming_events=["yoga-morning-01", "sports-tournament-01"]
    ),
}


# ─────────────────────────────────────────────
# DEADLINES
# ─────────────────────────────────────────────

DEADLINES = {
    "dl-001": Deadline(
        deadline_id="dl-001",
        title="Machine Learning Assignment Submission",
        type="academic",
        due_date=datetime(2026, 3, 27, 23, 59),
        student_id="student-001",
        is_completed=False
    ),
    "dl-002": Deadline(
        deadline_id="dl-002",
        title="Internship Application — Google STEP",
        type="internship",
        due_date=datetime(2026, 3, 28, 23, 59),
        student_id="student-001",
        is_completed=False
    ),
    "dl-003": Deadline(
        deadline_id="dl-003",
        title="Hackathon Team Registration",
        type="fest",
        due_date=datetime(2026, 3, 27, 18, 0),
        student_id="student-001",
        is_completed=False
    ),
    "dl-004": Deadline(
        deadline_id="dl-004",
        title="Drama Club Script Submission",
        type="club",
        due_date=datetime(2026, 3, 26, 17, 0),
        student_id="student-002",
        is_completed=False
    ),
    "dl-005": Deadline(
        deadline_id="dl-005",
        title="Mid Semester Exam — Data Structures",
        type="academic",
        due_date=datetime(2026, 3, 29, 9, 0),
        student_id="student-002",
        is_completed=False
    ),
    "dl-006": Deadline(
        deadline_id="dl-006",
        title="Cultural Fest Stall Registration",
        type="fest",
        due_date=datetime(2026, 3, 28, 12, 0),
        student_id="student-002",
        is_completed=False
    ),
    "dl-007": Deadline(
        deadline_id="dl-007",
        title="Photography Competition Entry",
        type="club",
        due_date=datetime(2026, 3, 27, 20, 0),
        student_id="student-004",
        is_completed=False
    ),
    "dl-008": Deadline(
        deadline_id="dl-008",
        title="Sports Council Annual Report",
        type="club",
        due_date=datetime(2026, 3, 30, 17, 0),
        student_id="student-004",
        is_completed=False
    ),
}


# ─────────────────────────────────────────────
# STUDENTS
# Two contrast students A and B + two extras
# ─────────────────────────────────────────────

STUDENTS = {
    # Student A — Tech + career focused, avoids mornings
    "student-001": StudentProfile(
        student_id="student-001",
        name="Arjun",
        year=2,
        enrolled_clubs=["coding-society", "entrepreneurship-cell"],
        registered_events=["ai-workshop-01", "founders-talk-01"],
        academic_deadlines=["dl-001", "dl-002", "dl-003"],
        join_date=datetime(2024, 8, 1),
        interests=["tech", "entrepreneurship"]
    ),
    # Student B — Arts + social, active morning person
    "student-002": StudentProfile(
        student_id="student-002",
        name="Priya",
        year=2,
        enrolled_clubs=["drama-club", "debate-society", "entrepreneurship-cell"],
        registered_events=["open-mic-01", "debate-01", "founders-talk-01"],
        academic_deadlines=["dl-004", "dl-005", "dl-006"],
        join_date=datetime(2024, 8, 1),
        interests=["arts", "cultural"]
    ),
    # Student C — Fresher (for freshers mode testing)
    "student-003": StudentProfile(
        student_id="student-003",
        name="Rahul",
        year=1,
        enrolled_clubs=["coding-society"],
        registered_events=["ai-workshop-01"],
        academic_deadlines=[],
        join_date=datetime(2026, 3, 1),   # joined recently → fresher mode
        interests=["tech"]
    ),
    # Student D — Sports + arts
    "student-004": StudentProfile(
        student_id="student-004",
        name="Sneha",
        year=3,
        enrolled_clubs=["photography-club", "sports-council", "drama-club"],
        registered_events=["photography-walk-01", "yoga-morning-01", "open-mic-01"],
        academic_deadlines=["dl-007", "dl-008"],
        join_date=datetime(2023, 8, 1),
        interests=["arts", "sports"]
    ),
}


# ─────────────────────────────────────────────
# QUERY FUNCTIONS
# ─────────────────────────────────────────────

def get_all_events() -> list[Event]:
    return list(EVENTS.values())


def get_events_by_category(category: str) -> list[Event]:
    return [e for e in EVENTS.values() if e.category == category]


def get_upcoming_deadlines(student_id: str, days: int = 7) -> list[Deadline]:
    from datetime import timedelta
    now = datetime.now()
    cutoff = now + timedelta(days=days)
    return [
        d for d in DEADLINES.values()
        if d.student_id == student_id
        and now <= d.due_date <= cutoff
        and not d.is_completed
    ]


def get_student_profile(student_id: str) -> StudentProfile | None:
    return STUDENTS.get(student_id)


def get_club_members(club_id: str) -> list[str]:
    club = CLUBS.get(club_id)
    return club.members if club else []


def get_events_for_club(club_id: str) -> list[Event]:
    club = CLUBS.get(club_id)
    if not club:
        return []
    return [EVENTS[eid] for eid in club.upcoming_events if eid in EVENTS]


def get_student_clubs(student_id: str) -> list[Club]:
    return [
        c for c in CLUBS.values()
        if student_id in c.members
    ]


def get_all_students() -> list[StudentProfile]:
    return list(STUDENTS.values())


def get_space(space_id: str) -> CampusSpace | None:
    return SPACES.get(space_id)


def is_fresher(student_id: str, fresher_window_days: int = 30) -> bool:
    from datetime import timedelta
    student = STUDENTS.get(student_id)
    if not student:
        return False
    return datetime.now() - student.join_date <= timedelta(days=fresher_window_days)


def get_cascade_window(student_id: str, days: int = 7) -> dict:
    """Check if student has 3+ deadlines colliding in next N days"""
    upcoming = get_upcoming_deadlines(student_id, days)
    return {
        "cascade": len(upcoming) >= 3,
        "count": len(upcoming),
        "items": upcoming,
        "alert": (
            f"⚠️ You have {len(upcoming)} deadlines in the next {days} days!"
            if len(upcoming) >= 3 else None
        )
    }
