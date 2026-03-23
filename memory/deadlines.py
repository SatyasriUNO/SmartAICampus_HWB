from datetime import datetime

def check_deadline_collisions(deadlines: list, today: datetime) -> dict:
    upcoming = []
    alerts = []

    for d in deadlines:
        due = datetime.fromisoformat(d["due_date"])
        days_left = (due - today).days

        if 0 <= days_left <= 7:
            upcoming.append({**d, "days_left": days_left})

        if days_left <= 2:
            alerts.append(f"⚠️ {d['title']} is due in {days_left} day(s)")

    collision = len([d for d in upcoming if d["days_left"] <= 3]) >= 2

    return {
        "upcoming": upcoming,
        "alerts": alerts,
        "collision_detected": collision
    }