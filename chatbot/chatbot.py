"""
chatbot.py — SadakWatch AI
Main chatbot engine.
Flow: User Message → Intent Classifier → DB Query → Groq LLM → Response
Offline fallback: If no internet/API key → use DB text directly.
"""

import os
import json
import requests
from intent_classifier import classify_intent
from db_query_handler  import handle_intent

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL    = "llama3-8b-8192"   # free, fast

SYSTEM_PROMPT = """You are SadakWatch AI — an intelligent road safety and accountability assistant for India.
You help citizens understand road information, track public spending, and report road issues.

Your personality:
- Helpful, direct, and factual
- Bilingual: respond in the same language the user uses (Hindi or English)
- Never make up data — only use the structured data provided to you
- Always mention the source document when sharing budget information (judges specifically check this)
- Always give the exact authority name, officer name, and contact when routing complaints

When given structured road data, format your response clearly with:
- Road type and contractor info
- DLP status (Defect Liability Period — contractor's responsibility window)
- Budget with source document
- Exact complaint authority

Keep responses concise but complete. Use emojis sparingly for readability.
Never say "I don't know" — if data is not available, explain what the user can do next.
"""


# ─────────────────────────────────────────────────────────────────────────────
# ONLINE MODE — Groq API
# ─────────────────────────────────────────────────────────────────────────────

def call_groq(user_message: str, db_context: str) -> str:
    """Call Groq API with user message + DB data as context."""
    if not GROQ_API_KEY:
        return None  # trigger offline fallback

    prompt = f"""User asked: "{user_message}"

Here is the relevant data from our database:
{db_context}

Please provide a clear, helpful response based on this data.
If budget is mentioned, always include the source document.
If complaint routing is mentioned, always include the officer name and phone number."""

    try:
        response = requests.post(
            GROQ_ENDPOINT,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "model":    GROQ_MODEL,
                "messages": [
                    {"role": "system",  "content": SYSTEM_PROMPT},
                    {"role": "user",    "content": prompt},
                ],
                "max_tokens":  512,
                "temperature": 0.3,   # low temp = factual, consistent
            },
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None
    except Exception:
        return None   # network error → offline fallback


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CHAT FUNCTION — called by Streamlit UI
# ─────────────────────────────────────────────────────────────────────────────

def chat(user_message: str, extra: dict = None) -> dict:
    """
    Full pipeline: message → intent → DB → LLM → response.

    Args:
        user_message: raw user input (Hindi or English)
        extra:        optional dict with lat, lon, description, reporter_contact

    Returns:
        {
            "response":     str,   # final text shown to user
            "intent":       str,
            "data":         dict,  # structured data (used by UI cards)
            "mode":         str,   # "online" | "offline"
            "complaint_id": str | None
        }
    """
    extra = extra or {}

    # Step 1: Classify intent
    classified = classify_intent(user_message)
    intent     = classified["intent"]
    entities   = classified["entities"]

    # Step 2: Query DB
    db_result = handle_intent(intent, entities, extra)

    # Step 3: Build context string for LLM
    db_context = _build_context_string(db_result)

    # Step 4: Try Groq API (online mode)
    llm_response = call_groq(user_message, db_context)
    mode = "online" if llm_response else "offline"

    # Step 5: Offline fallback — use pre-formatted DB text directly
    final_response = llm_response or db_result.get("message", "Data not found.")

    return {
        "response":     final_response,
        "intent":       intent,
        "entities":     entities,
        "data":         db_result.get("data", {}),
        "status":       db_result.get("status"),
        "mode":         mode,
        "complaint_id": db_result.get("complaint_id"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# CONTEXT BUILDER — converts DB result dict to readable string for LLM
# ─────────────────────────────────────────────────────────────────────────────

def _build_context_string(db_result: dict) -> str:
    status = db_result.get("status")
    data   = db_result.get("data", {})

    if status in ("not_found", "unknown", "error"):
        return "No relevant data found in database."

    if status == "offline_fallback":
        return db_result.get("message", "")

    if isinstance(data, list):
        # Multiple results
        lines = []
        for item in data[:5]:  # limit to 5 for context length
            lines.append(json.dumps(item, default=str))
        return "\n".join(lines)

    # Single result dict
    return json.dumps(data, default=str, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# CONVERSATION HISTORY MANAGER (for Streamlit session state)
# ─────────────────────────────────────────────────────────────────────────────

class ConversationManager:
    """
    Maintains chat history for multi-turn conversations.
    Stored in Streamlit session_state.
    """
    def __init__(self):
        self.history = []

    def add_user(self, message: str):
        self.history.append({"role": "user", "content": message})

    def add_bot(self, message: str, intent: str, mode: str):
        self.history.append({
            "role":    "assistant",
            "content": message,
            "intent":  intent,
            "mode":    mode,
        })

    def get_history(self) -> list:
        return self.history

    def clear(self):
        self.history = []

    def last_context(self) -> str:
        """Last 3 exchanges as context for next message."""
        recent = self.history[-6:]  # 3 turns
        return "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )


# ─────────────────────────────────────────────────────────────────────────────
# SUGGESTED QUESTIONS — shown in UI as quick-tap buttons
# ─────────────────────────────────────────────────────────────────────────────

SUGGESTED_QUESTIONS = {
    "en": [
        "Tell me about NH-44",
        "How much was spent on NH-48 Pune?",
        "Who should I complain to for SH-18 in MP?",
        "What is Ashoka Buildcon's accountability score?",
        "Show all contractors ranked by score",
    ],
    "hi": [
        "NH-44 ke baare mein batao",
        "NH-48 Pune pe kitna paisa kharch hua?",
        "SH-18 MP ke liye shikayat kahan karein?",
        "Ashoka Buildcon ka score kya hai?",
        "Sabse achhe aur bure contractors kaun hain?",
    ],
}

def get_suggestions(lang: str = "en") -> list[str]:
    return SUGGESTED_QUESTIONS.get(lang, SUGGESTED_QUESTIONS["en"])


# ─────────────────────────────────────────────────────────────────────────────
# QUICK TEST — terminal chatbot
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== SadakWatch AI — Terminal Test ===")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        result = chat(user_input)
        print(f"\n🤖 SadakWatch [{result['mode'].upper()}]:")
        print(f"   Intent: {result['intent']}")
        print(f"   {result['response']}\n")
        if result.get("complaint_id"):
            print(f"   📋 Complaint ID: {result['complaint_id']}\n")