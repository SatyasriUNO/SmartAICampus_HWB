# tests/test_agent.py

from backend.agent import run_agent

print("=" * 60)
print("TEST 1 — Proactive mode (no input)")
print("=" * 60)
response = run_agent("student-001")
print(f"🤖 Agent: {response.message}")
print(f"   Proactive: {response.proactive}")

print("\n" + "=" * 60)
print("TEST 2 — Student asks a question")
print("=" * 60)
response = run_agent("student-001", "what events should I attend this week?")
print(f"🤖 Agent: {response.message}")

print("\n" + "=" * 60)
print("TEST 3 — Different student, same question")
print("=" * 60)
response = run_agent("student-002", "what events should I attend this week?")
print(f"🤖 Agent: {response.message}")

print("\n" + "=" * 60)
print("TEST 4 — Fresher student")
print("=" * 60)
response = run_agent("student-003", "I just joined college, what should I do?")
print(f"🤖 Agent: {response.message}")
