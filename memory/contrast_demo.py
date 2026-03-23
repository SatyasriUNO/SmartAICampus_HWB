# memory/contrast_demo.py — REPLACE ONLY THE TOP IMPORTS

from backend.agent import run_agent          # ← changed
from memory.retain import retain as store_memory  # ← changed

# rest of file stays exactly the same

# ── Setup Student A ──────────────────────────────
store_memory(
    bank_id="student_A",
    content="""
    Student is passionate about technology and artificial intelligence.
    Attended AI Workshop and enjoyed it. Member of Tech Club and Coding Society.
    Prefers evening events. Has been asking about hackathons and internships.
    Wants to build projects and improve coding skills.
    """
)

# ── Setup Student B ──────────────────────────────
store_memory(
    bank_id="student_B",
    content="""
    Student loves music and creative arts.
    Member of Music Club and Arts Club.
    Attended Music Fest last semester and loved it.
    Prefers morning events. Interested in photography and dance.
    Dislikes technical and coding events.
    """
)

# ── Same Question, Both Students ─────────────────
question = "What should I do this week on campus?"

print("=" * 50)
print("STUDENT A — Tech/AI Focused")
print("=" * 50)
response_A = run_agent("student_A", question)
print(response_A)

print("\n" + "=" * 50)
print("STUDENT B — Music/Arts Focused")
print("=" * 50)
response_B = run_agent("student_B", question)
print(response_B)
