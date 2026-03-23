# backend/llm.py

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# Groq client — single instance
# ─────────────────────────────────────────────

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a Smart Campus AI Assistant.
You know the student personally — their interests, habits, clubs, events attended, and deadlines.
You speak like a helpful, friendly senior student — not a bot.
Be concise, specific, and proactive.
Never say generic things like "here are some events you might like."
Always reference something specific from the student's memory or context.
If the student hasn't asked anything, open with the most relevant thing they need to know right now.
"""

def call_llm(
    user_message: str,
    memory_context: str,
    student_name: str,
    extra_context: str = ""
) -> str:
    """
    Core LLM call. Injects memory context into every request.
    """

    full_context = f"""
Student Name: {student_name}

--- MEMORY CONTEXT ---
{memory_context}

--- ADDITIONAL CONTEXT ---
{extra_context}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_context},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content


def call_llm_structured(prompt: str) -> str:
    """
    For internal logic calls — drift detection, 
    opportunity surfacing etc.
    No memory injection, just raw prompt → response.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=300
    )
    return response.choices[0].message.content
