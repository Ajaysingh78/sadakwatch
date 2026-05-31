"""
intent_classifier.py — SadakWatch AI
Detects intent from user message (Hindi + English both).
Rule-based first (offline works), LLM fallback when online.

5 Intents:
    road_lookup      — road info, contractor, DLP status
    budget_query     — sanctioned/spent/funding source
    complaint_report — user wants to file a new complaint
    complaint_route  — who to complain to, which authority
    contractor_check — contractor score, history
"""

import re

# ─────────────────────────────────────────────────────────────────────────────
# KEYWORD MAPS — Hindi + English both covered
# ─────────────────────────────────────────────────────────────────────────────

INTENT_KEYWORDS = {

    "road_lookup": [
        # English
        "road info", "road details", "tell me about", "road condition",
        "which contractor", "who built", "last repair", "repair date",
        "dlp", "defect liability", "road type", "road status",
        "nh-", "sh-", "highway info", "road data", "road history",
        # Hindi
        "sadak ki jankari", "sadak ke baare mein", "sadak batao",
        "contractor kaun", "kisne banaya", "kab repair", "repair kab hua",
        "sadak ki halat", "sadak kaisi hai", "dlp kya hai",
        "kis contractor ne", "kab bani", "kitni purani",
    ],

    "budget_query": [
        # English
        "budget", "how much money", "funds", "sanctioned", "spent",
        "expenditure", "cost", "amount", "funding source", "where money",
        "utilization", "allocated", "crore", "lakh",
        "cag", "source document", "audit",
        # Hindi
        "kitna paisa", "paisa kahan se", "budget kya hai", "budget kitna",
        "kitna kharch", "kharcha", "paisa", "funding", "sanctioned amount",
        "rakam", "rajya sarkar", "kendriya", "nabard", "pmgsy fund",
        "source kya hai", "paise ka hisaab",
    ],

    "complaint_report": [
        # English
        "report", "complaint", "file complaint", "submit complaint",
        "pothole", "broken road", "damaged", "accident prone",
        "bad road", "poor condition", "waterlogging", "missing signage",
        "broken divider", "i want to complain", "report issue",
        # Hindi
        "shikayat", "shikayat karna", "complaint karna", "report karna",
        "gadha", "gaddha", "khaddha", "toot gayi sadak", "kharab sadak",
        "accident ho raha", "paani bharta hai", "board nahi hai",
        "divider tuta", "problem hai sadak mein", "issue hai",
    ],

    "complaint_route": [
        # English
        "who to contact", "where to complain", "authority", "officer",
        "executive engineer", "ee contact", "contact number",
        "nhai complaint", "pwd complaint", "district collector",
        "where do i report", "complaint number", "helpline",
        "responsible person", "who is responsible", "whom to call",
        # Hindi
        "kahan shikayat karein", "kisko batayein", "kisse milein",
        "adhikari kaun", "executive engineer kaun", "contact kahan",
        "nhai ko kaise", "pwd ka number", "collector se milna",
        "zimmedar kaun", "jawabdeh kaun", "kahan call karein",
        "helpline number", "contact details chahiye",
    ],

    "contractor_check": [
        # English
        "contractor score", "contractor rating", "contractor history",
        "is contractor good", "contractor performance", "past work",
        "contractor violations", "dlp violation", "overrun",
        "accountability score", "grade", "contractor record",
        "which contractors", "all contractors", "leaderboard",
        # Hindi
        "contractor kaisa hai", "contractor ka record", "contractor ki history",
        "score kya hai", "rating kya hai", "achha contractor",
        "contractor ne kya kiya", "kitne roads banaye", "kaam kaisa",
        "accountability", "dlp violation contractor", "worst contractor",
        "best contractor", "sab contractors",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# ENTITY EXTRACTORS — pull road name, state, complaint type from message
# ─────────────────────────────────────────────────────────────────────────────

# Road name patterns
ROAD_PATTERNS = [
    r"\b(nh[-\s]?\d+[a-z]?)\b",          # NH-44, NH44, NH 44
    r"\b(sh[-\s]?\d+[a-z]?)\b",          # SH-18, SH18
    r"\b(mdr[-\s]?\d+)\b",               # MDR-12
    r"(pmgsy\s+\w+)",                     # PMGSY Sehore
    r"([\w\s]+ road)",                    # TT Nagar Road
    r"([\w\s]+ highway)",                 # some highway
    r"([\w\s]+ expressway)",              # expressway
]

# Indian states
STATE_NAMES = {
    "mp": "Madhya Pradesh", "madhya pradesh": "Madhya Pradesh",
    "mh": "Maharashtra",    "maharashtra": "Maharashtra",
    "up": "Uttar Pradesh",  "uttar pradesh": "Uttar Pradesh",
    "rj": "Rajasthan",      "rajasthan": "Rajasthan",
    "tn": "Tamil Nadu",     "tamil nadu": "Tamil Nadu",
    "dl": "Delhi",          "delhi": "Delhi",
    "ap": "Andhra Pradesh", "andhra": "Andhra Pradesh",
    "bhopal": "Madhya Pradesh",
    "pune": "Maharashtra",
    "mumbai": "Maharashtra",
    "jaipur": "Rajasthan",
    "lucknow": "Uttar Pradesh",
    "chennai": "Tamil Nadu",
}

# Complaint types
COMPLAINT_TYPES = {
    "pothole": ["pothole", "gaddha", "gadha", "khaddha", "hole in road"],
    "waterlogging": ["waterlog", "paani bhar", "flood", "water on road", "drainage"],
    "missing_signage": ["sign", "board", "signage", "speed limit", "no board"],
    "broken_divider": ["divider", "median", "barrier broken", "divider tuta"],
    "road_damage": ["broken road", "toot", "kharab", "damaged", "crack"],
    "poor_lighting": ["light nahi", "dark road", "no street light", "lighting"],
}

SEVERITY_MAP = {
    "Critical": ["accident", "death", "fatality", "bahut kharab", "emergency",
                 "critical", "head-on", "collision"],
    "High":     ["high", "bada", "large", "dangerous", "unsafe", "bahut bada"],
    "Low":      ["small", "minor", "thoda", "chhota", "not urgent"],
}


# ─────────────────────────────────────────────────────────────────────────────
# CORE CLASSIFIER
# ─────────────────────────────────────────────────────────────────────────────

def classify_intent(message: str) -> dict:
    """
    Rule-based intent classifier. Works fully offline.
    
    Returns:
        {
            "intent":     str,   # one of 5 intents
            "confidence": float, # 0.0 - 1.0
            "entities":   dict,  # extracted road, state, etc.
            "raw":        str    # original message
        }
    """
    msg_lower = message.lower().strip()

    # Score each intent
    scores = {intent: 0 for intent in INTENT_KEYWORDS}
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in msg_lower:
                scores[intent] += 1

    best_intent = max(scores, key=scores.get)
    best_score  = scores[best_intent]
    total_hits  = sum(scores.values()) or 1
    confidence  = round(best_score / total_hits, 2) if best_score > 0 else 0.0

    # If no keywords matched at all → mark as unknown
    if best_score == 0:
        best_intent = "unknown"
        confidence  = 0.0

    entities = extract_entities(msg_lower, best_intent)

    return {
        "intent":     best_intent,
        "confidence": confidence,
        "entities":   entities,
        "raw":        message,
    }


def extract_entities(msg_lower: str, intent: str) -> dict:
    """Extract road name, state, complaint type from message."""
    entities = {}

    # Road name/number
    for pattern in ROAD_PATTERNS:
        match = re.search(pattern, msg_lower, re.IGNORECASE)
        if match:
            entities["road_query"] = match.group(1).strip()
            break

    # State detection
    for key, full_name in STATE_NAMES.items():
        if key in msg_lower:
            entities["state"] = full_name
            break

    # Road type
    if re.search(r"\bnh\b|\bnational highway\b", msg_lower):
        entities["road_type"] = "NH"
    elif re.search(r"\bsh\b|\bstate highway\b", msg_lower):
        entities["road_type"] = "SH"
    elif re.search(r"\bvillage\b|\bpmgsy\b|\bgram sadak\b", msg_lower):
        entities["road_type"] = "Village"
    elif re.search(r"\burban\b|\bcity road\b|\bmunicipa\b", msg_lower):
        entities["road_type"] = "Urban"

    # Complaint type (for complaint intents)
    if intent in ("complaint_report", "complaint_route"):
        for ctype, keywords in COMPLAINT_TYPES.items():
            if any(kw in msg_lower for kw in keywords):
                entities["complaint_type"] = ctype
                break

        # Severity
        entities["severity"] = "Medium"  # default
        for sev, keywords in SEVERITY_MAP.items():
            if any(kw in msg_lower for kw in keywords):
                entities["severity"] = sev
                break

    # Contractor name (for contractor_check)
    if intent == "contractor_check":
        known_contractors = [
            "ashoka", "l&t", "irb", "gr infra", "hg infra",
            "pnc", "dilip buildcon", "kcc", "apco", "j kumar",
        ]
        for name in known_contractors:
            if name in msg_lower:
                entities["contractor_name"] = name
                break

    # Country (for global applicability)
    global_countries = ["uk", "united kingdom", "usa", "united states",
                        "germany", "australia", "france"]
    for country in global_countries:
        if country in msg_lower:
            entities["country"] = country
            break

    return entities


# ─────────────────────────────────────────────────────────────────────────────
# HINDI TRANSLITERATION NORMALIZER
# Handles common spelling variations in Hinglish
# ─────────────────────────────────────────────────────────────────────────────

HINDI_NORMALIZE = {
    "sadak":    "road",
    "raasta":   "road",
    "shikayat": "complaint",
    "paisa":    "money",
    "kitna":    "how much",
    "kharab":   "bad condition",
    "toot":     "broken",
    "gaddha":   "pothole",
    "khaddha":  "pothole",
    "gadha":    "pothole",
    "bijli":    "lighting",
    "pani":     "water",
    "paani":    "water",
}

def normalize_message(message: str) -> str:
    """Normalize Hindi transliterations to English equivalents."""
    msg = message.lower()
    for hindi, english in HINDI_NORMALIZE.items():
        msg = msg.replace(hindi, english)
    return msg


# ─────────────────────────────────────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_messages = [
        "NH-44 ke baare mein batao",
        "Ashoka Buildcon ka score kya hai?",
        "Budget kitna tha NH-44 ka aur paisa kahan se aaya?",
        "Pothole hai road pe, shikayat karna hai",
        "Kahan complaint karein NHAI ko?",
        "Tell me about NH-48 Pune stretch",
        "Who is responsible for SH-18 in Madhya Pradesh?",
        "How much was spent on NH-19?",
        "Contractor kaisa hai Dilip Buildcon?",
        "Hello, mujhe kuch jaanna hai",  # unknown intent test
    ]

    print("=== Intent Classifier Test ===\n")
    for msg in test_messages:
        result = classify_intent(msg)
        print(f"MSG:    {msg}")
        print(f"INTENT: {result['intent']} (confidence: {result['confidence']})")
        print(f"ENT:    {result['entities']}")
        print()