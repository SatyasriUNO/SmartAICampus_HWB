# memory/schemas.py — REPLACE ENTIRE FILE WITH THIS

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MemoryEntry(BaseModel):
    student_id: str
    action: str           # attended, ignored, joined, dropped, queried
    target_type: str      # event, club, deadline, space
    target_name: str
    category: str         # tech, arts, sports, entrepreneurship, cultural
    timestamp: datetime
    time_of_day: str      # morning, afternoon, evening, night
    metadata: Optional[dict] = {}
