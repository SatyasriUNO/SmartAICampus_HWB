# 🎓 Smart Campus AI Assistant
### *A memory-driven campus companion that learns who you are — without ever asking.*

---

> **"Same campus. Same events. Same query. Completely different experience."**
> That's not a feature — that's Hindsight memory at work.

---

## 📌 Overview

The Smart Campus AI Assistant is an AI-powered personal companion for university students, built on top of **[Hindsight](https://github.com/vectorize-io/hindsight)** — a state-of-the-art agent memory system developed by Vectorize. Unlike conventional campus bots that forget everything between sessions, this assistant *learns* — silently, persistently, and without ever asking the student to fill out a profile.

It remembers what events you attended, what you ignored, which clubs you dropped, and when your deadlines collide. Over time, it builds a behavioral fingerprint unique to each student and uses it to deliver recommendations, reminders, and nudges that feel genuinely personal.

This project was built as part of the **Hindsight Hackathon**, under the *Smart Campus AI Assistant* problem statement.

---

## ✨ Key Features & Novelty Points

### 🔄 Interest Drift Detection
Student interests shift naturally over a semester. A student who started exploring debate gradually moves toward entrepreneurship. The assistant detects this behavioral drift from interaction patterns and silently updates recommendations — no manual profile update ever required.

### 🚀 Proactive Anticipation
The assistant doesn't wait to be asked. Every session opens with the most relevant thing the student needs to know right now — an upcoming deadline, a club event today, or a registration closing tomorrow. Zero prompts. Maximum relevance.

### 🎭 Two-Student Contrast Demo
The same question — *"What should I do this evening?"* — yields completely different responses for two students on the same campus, with access to the same event list, based purely on their Hindsight memory. This single demonstration makes personalization tangible and immediately convincing to anyone watching.

### 🔗 Cross-Interest Opportunity Surfacing
A student who attends coding workshops, follows the entrepreneurship cell, and asks about internships has an underlying pattern — career-focused tech growth. The assistant connects these dots and surfaces a startup pitch competition they never thought to search for.

### 🔇 Silent Avoidance Learning
The assistant learns not just from what students engage with, but from what they consistently ignore. A student who never attends morning events, always skips sports, and drops clubs after one meeting tells the assistant something important — and future recommendations adjust silently, without ever making the student explain themselves.

### 🌱 Freshers Guided Discovery Mode
New students receive a 30-day memory-building journey. Each week, the assistant nudges them toward one new club, one new space, one new activity — and remembers what resonated. By the end of month one, the assistant knows the student well enough to make genuinely useful, personalized recommendations.

### 👥 Social Graph Nudging
When two students share overlapping interest memories but have never interacted, the assistant creates a natural, privacy-safe bridge — routing the connection through shared activities rather than exposing any individual's data.

### 📅 Deadline Cascade Awareness
Campus deadlines rarely exist in isolation. The assistant cross-references academic deadlines, club schedules, and fest registrations simultaneously — alerting the student when multiple things are colliding in the same week, before it becomes a crisis.

### 📊 Behavior-Based Recommendations
Recommendations are derived entirely from behavioral patterns — what you do, not what you say. Stated preferences are irrelevant; actions are everything.

### ⏰ Context-Aware Suggestions
The assistant applies intelligent temporal filters. During exam week, event suggestions are reduced and limited to short, low-commitment activities. During free periods, the full recommendation engine runs without restriction.

### 🗺️ Campus Mapping Twist *(Bonus)*
Event suggestions are paired with real campus location data, enabling the assistant to suggest routes and nearby spaces alongside activity recommendations — directly leveraging spatial awareness for a richer experience.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Aditi)                      │
│              Chat UI · Dashboard · Demo Panel            │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────┐
│                  REST API — FastAPI                       │
│   /chat · /recommendations · /reminders · /nudges        │
│   /drift · /avoidance · /demo/contrast · /profile        │
└────────────────────────┬────────────────────────────────┘
                         │ imports
┌────────────────────────▼────────────────────────────────┐
│              Backend / Core Engine                        │
│                                                          │
│  agent.py          Core agent loop                       │
│  recommender.py    Scoring + ranking engine              │
│  filters.py        Context-aware filter pipeline         │
│  reminders.py      Smart reminders + cascade detector    │
│  social.py         Social graph nudging                  │
│  database.py       Mock campus data                      │
│  llm.py            Groq LLM integration                  │
└────────────────────────┬────────────────────────────────┘
                         │ imports
┌────────────────────────▼────────────────────────────────┐
│              Memory Layer — Hindsight                     │
│                                                          │
│  retain.py         Store interactions to Hindsight       │
│  recall.py         Fetch ranked memories from Hindsight  │
│  drift.py          Interest drift detection              │
│  avoidance.py      Silent avoidance pattern learning     │
│  cross_interest.py Cross-interest opportunity surfacing  │
│  anticipation.py   Proactive trigger engine              │
│  freshers.py       30-day guided discovery arc           │
│  schemas.py        MemoryEntry data model                │
└────────────────────────┬────────────────────────────────┘
                         │ API calls
┌────────────────────────▼────────────────────────────────┐
│              Hindsight Cloud (Vectorize)                  │
│     retain() · recall() · TEMPR multi-strategy search    │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Memory | [Hindsight](https://hindsight.vectorize.io/) by Vectorize |
| LLM | [Groq](https://groq.com/) — `llama-3.3-70b-versatile` |
| Backend | Python 3.10+ · FastAPI · Uvicorn |
| Data Validation | Pydantic v2 |
| Frontend | HTML · CSS · JavaScript |
| Environment | python-dotenv |

---

## 📁 Project Structure

```
campai/
├── .env                      # API keys (never commit this)
├── main.py                   # Server entry point
├── requirements.txt          # Dependencies
│
├── backend/
│   ├── models.py             # Pydantic data models
│   ├── database.py           # Mock campus data + query functions
│   ├── agent.py              # Core agent loop
│   ├── recommender.py        # Recommendation engine
│   ├── filters.py            # Context-aware filter pipeline
│   ├── reminders.py          # Smart reminder scheduler
│   ├── social.py             # Social graph nudging
│   ├── llm.py                # Groq LLM client
│   └── api.py                # FastAPI REST endpoints
│
├── memory/
│   ├── schemas.py            # MemoryEntry model
│   ├── retain.py             # Hindsight retain wrappers
│   ├── recall.py             # Hindsight recall wrappers
│   ├── drift.py              # Interest drift detection
│   ├── avoidance.py          # Avoidance pattern learning
│   ├── cross_interest.py     # Opportunity surfacing
│   ├── anticipation.py       # Proactive trigger engine
│   ├── freshers.py           # 30-day discovery arc
│   └── contrast_demo.py      # Two-student judge demo
│
└── tests/
    ├── test_models.py
    ├── test_database.py
    ├── test_agent.py
    ├── test_recommender.py
    ├── test_filters.py
    ├── test_reminders.py
    ├── test_social.py
    ├── test_api.py
    └── test_e2e.py
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- A [Hindsight Cloud](https://ui.hindsight.vectorize.io/signup) account
- A [Groq](https://console.groq.com/) API key

### 1. Clone the repository
```bash
git clone https://github.com/Bikash-Prem/Smart_Ai_College.git
cd Smart_Ai_College/campai
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root of `campai/`:
```env
HINDSIGHT_BASE_URL=https://your-hindsight-cloud-url
HINDSIGHT_API_KEY=your-hindsight-api-key
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

> 💡 Apply promo code `MEMHACK315` in your Hindsight Cloud billing section for $50 in free credits.

### 5. Run the server
```bash
python main.py
```

The server starts at `http://localhost:8000`.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/docs` | Interactive API documentation |
| `GET` | `/profile/{id}` | Student profile + inferred interests |
| `GET` | `/students` | List all students |
| `POST` | `/chat` | Main agent chat (empty message = proactive) |
| `GET` | `/recommendations/{id}` | Filtered, ranked event recommendations |
| `GET` | `/reminders/{id}` | Smart reminders + cascade detection |
| `GET` | `/deadlines/{id}` | Upcoming deadlines with urgency levels |
| `GET` | `/drift/{id}` | Interest drift analysis |
| `GET` | `/avoidance/{id}` | Silent avoidance flags |
| `GET` | `/nudges/{id}` | Social graph nudges |
| `POST` | `/retain` | Manually store a memory |
| `GET` | `/demo/contrast` | **Judge demo — two-student contrast** |
| `GET` | `/demo/events` | All campus events |

### Example — Chat Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student-001", "message": ""}'
```

### Example — Proactive Response
```json
{
  "student_id": "student-001",
  "student_name": "Arjun",
  "message": "Hey Arjun! Quick heads up — your ML assignment is due in 2 days and your Google STEP application closes tomorrow. Also, the Coding Society has the 24hr Hackathon tonight at 9PM.",
  "proactive": true,
  "timestamp": "2026-03-23T18:44:00"
}
```

---

## 🎬 The Judge Demo

Hit this single endpoint to see the core value proposition in action:

```
GET http://localhost:8000/demo/contrast
```

Two students. Same campus. Same event list. Same query.
**Completely different recommendations** — driven entirely by Hindsight memory.

```
🧑 ARJUN (tech + entrepreneurship)        🧑 PRIYA (arts + cultural)
─────────────────────────────────         ──────────────────────────
→ Startup Pitch Competition               → Cultural Fest Open Mic
→ 24hr Campus Hackathon                   → Drama Club Rehearsal
→ Founders Talk: Building in College      → Inter-College Debate

"Your ML assignment is due in 2 days.     "Your Drama script is due tomorrow.
 Don't miss the Hackathon registration."   Attend rehearsal then submit."
```

---

## 🧪 Running Tests

```bash
# Memory layer — tests Hindsight retain/recall
python -m tests.test_memory

# Agent loop — tests all 4 student scenarios
python -m tests.test_agent

# Full end-to-end pipeline
python -m tests.test_e2e
```

---

## 🔗 Hindsight Integration

This project uses [Hindsight](https://github.com/vectorize-io/hindsight) for persistent agent memory. Every student interaction is retained as a structured memory entry and recalled via TEMPR — Hindsight's four-strategy parallel retrieval system combining semantic, keyword, graph, and temporal search.

The memory layer is fully encapsulated in the `memory/` module. Swapping between local and cloud Hindsight requires changing only the `.env` file — no code changes anywhere.

**Useful links:**
- 📖 [Hindsight Documentation](https://hindsight.vectorize.io/)
- 💻 [Hindsight GitHub](https://github.com/vectorize-io/hindsight)
- 🧠 [Agent Memory on Vectorize](https://vectorize.io/features/agent-memory)

---

## 👨‍💻 Team

| Member | Role |
|--------|------|
| **Satya** | AI/ML · Memory Layer · Backend Core Engine |
| **Bikash** | Backend · Agent Engine · Repo Setup |
| **Aditi** | Frontend · UI/UX |
| **Pramagdha** | Full Stack · API Integration |
| **Gouri** | Embedded · Campus Mapping |
| **Vaibhav** | Presentation · Content |
<p align="center">
  Built with 🧠 Hindsight Memory · Powered by Groq · Made at the Hindsight Hackathon
</p>
