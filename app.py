"""
app.py — SadakWatch AI
Streamlit frontend. Run with: streamlit run app.py
"""

import streamlit as st
import sys
import os
import folium
from streamlit_folium import st_folium
from datetime import datetime

# Path setup
sys.path.append(os.path.join(os.path.dirname(__file__), "chatbot"))
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))

from chatbot import chat, get_suggestions, ConversationManager
from db_helpers import get_all_contractors_ranked, search_road_flexible

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SadakWatch AI",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Root variables */
:root {
    --orange:  #FF6B35;
    --blue:    #1A1A2E;
    --green:   #00C896;
    --red:     #FF4444;
    --yellow:  #FFB800;
    --bg:      #0F0F1A;
    --card-bg: #1A1A2E;
    --border:  #2A2A3E;
    --text:    #E8E8F0;
    --muted:   #888899;
}

/* Global */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 1rem; }

/* Header */
.sw-header {
    background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 50%, #FFB800 100%);
    padding: 1.2rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.sw-header h1 {
    color: #0F0F1A;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
}
.sw-header p {
    color: #0F0F1Acc;
    margin: 0;
    font-size: 0.85rem;
}

/* Chat messages */
.user-msg {
    background: #2A2A3E;
    border-left: 3px solid var(--orange);
    padding: 0.8rem 1rem;
    border-radius: 0 10px 10px 0;
    margin: 0.5rem 0;
    margin-left: 2rem;
    font-size: 0.95rem;
}
.bot-msg {
    background: #1A1A2E;
    border-left: 3px solid var(--green);
    padding: 0.8rem 1rem;
    border-radius: 0 10px 10px 0;
    margin: 0.5rem 0;
    margin-right: 2rem;
    font-size: 0.95rem;
    white-space: pre-wrap;
}
.bot-msg-offline {
    border-left-color: var(--yellow);
}

/* Mode badge */
.mode-badge-online  { background: #00C89622; color: #00C896; padding: 2px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
.mode-badge-offline { background: #FFB80022; color: #FFB800; padding: 2px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }

/* Info card */
.info-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.8rem;
}
.info-card h4 {
    color: var(--orange);
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Score bar */
.score-bar-wrap { background: #2A2A3E; border-radius: 20px; height: 8px; margin: 4px 0; }
.score-bar-fill { height: 8px; border-radius: 20px; }

/* Suggestion chips */
.suggestion-chip {
    display: inline-block;
    background: #2A2A3E;
    border: 1px solid #3A3A4E;
    color: var(--text);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    cursor: pointer;
    margin: 2px;
}

/* Complaint ID */
.complaint-id {
    background: #00C89611;
    border: 1px solid #00C89644;
    color: #00C896;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #12121F;
    border-right: 1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────

if "messages"    not in st.session_state: st.session_state.messages    = []
if "lang"        not in st.session_state: st.session_state.lang        = "en"
if "last_data"   not in st.session_state: st.session_state.last_data   = {}
if "last_intent" not in st.session_state: st.session_state.last_intent = ""
if "online_mode" not in st.session_state: st.session_state.online_mode = bool(os.environ.get("GROQ_API_KEY"))

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="sw-header">
  <div>
    <h1>🛣️ SadakWatch AI</h1>
    <p>Road accountability chatbot — contractor tracking, budget transparency, complaint routing</p>
  </div>
  <div style="text-align:right">
    <p style="color:#0F0F1A88;font-size:0.75rem;">IIT Madras Road Safety Hackathon 2026</p>
    <p style="color:#0F0F1A;font-weight:600;font-size:0.8rem;">Powered by CoERS iRAD data</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT — 3 columns: chat | info cards | map
# ─────────────────────────────────────────────────────────────────────────────

col_chat, col_info, col_map = st.columns([2, 1.2, 1.5])

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Settings")

    # Language toggle
    lang_choice = st.radio("Language / भाषा", ["English", "हिंदी"], horizontal=True)
    st.session_state.lang = "hi" if "हिंदी" in lang_choice else "en"

    # Online/Offline indicator
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if groq_key:
        st.markdown('<span class="mode-badge-online">🟢 ONLINE — Groq AI Active</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="mode-badge-offline">🟡 OFFLINE — Rule-based Mode</span>', unsafe_allow_html=True)
        st.caption("Set GROQ_API_KEY to enable AI responses")

    st.divider()

    # Quick stats
    st.markdown("### 📊 Database Stats")
    try:
        contractors = get_all_contractors_ranked()
        st.metric("Contractors Tracked", len(contractors))
        avg_score = round(sum(c["accountability_score"] for c in contractors) / len(contractors), 1)
        st.metric("Avg Accountability Score", f"{avg_score}/10")
        poor = sum(1 for c in contractors if c["grade"] == "Poor")
        st.metric("Poor Grade Contractors", poor, delta=f"{poor} need action", delta_color="inverse")
    except Exception:
        st.caption("Run seed_data.py first")

    st.divider()

    # Complaint tracker
    st.markdown("### 📋 Track Complaint")
    track_id = st.text_input("Enter Complaint ID", placeholder="SW-2025-BPL-0021")
    if st.button("Track") and track_id:
        from db_helpers import get_complaint_status
        status = get_complaint_status(track_id.strip())
        if status:
            st.success(f"**{status['complaint_type']}** — {status['status']}")
            st.caption(f"Road: {status.get('road_name', 'N/A')}")
            st.caption(f"Officer: {status.get('engineer_name', 'N/A')}")
            if status.get("resolution_date"):
                st.caption(f"Resolved: {status['resolution_date']}")
        else:
            st.error("Complaint ID not found")

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages  = []
        st.session_state.last_data = {}
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# CHAT COLUMN
# ─────────────────────────────────────────────────────────────────────────────

with col_chat:
    st.markdown("#### 💬 Chat")

    # Suggestion chips
    suggestions = get_suggestions(st.session_state.lang)
    cols = st.columns(len(suggestions))
    for i, (col, sug) in enumerate(zip(cols, suggestions[:3])):
        with col:
            if st.button(sug, key=f"sug_{i}", use_container_width=True):
                st.session_state._pending_message = sug

    # Chat history display
    chat_container = st.container(height=420)
    with chat_container:
        if not st.session_state.messages:
            welcome = (
                "Namaste! Main **SadakWatch AI** hun. 🛣️\n\n"
                "Main aapko in sawaalon mein help kar sakta hun:\n"
                "• Kisi bhi road ki jankari (contractor, DLP status)\n"
                "• Budget aur funding source\n"
                "• Complaint kahan aur kise karein\n"
                "• Contractor accountability score\n\n"
                "Kuch poochiye — Hindi ya English mein!"
            ) if st.session_state.lang == "hi" else (
                "Hello! I'm **SadakWatch AI**. 🛣️\n\n"
                "I can help you with:\n"
                "• Road info — contractor, DLP status, condition\n"
                "• Budget & funding source (with source document)\n"
                "• Complaint routing — exact officer & contact\n"
                "• Contractor accountability scores\n\n"
                "Ask me anything in Hindi or English!"
            )
            st.markdown(f'<div class="bot-msg">{welcome}</div>', unsafe_allow_html=True)

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                mode_class = "bot-msg" if msg.get("mode") == "online" else "bot-msg bot-msg-offline"
                badge = (
                    '<span class="mode-badge-online">🟢 AI</span>'
                    if msg.get("mode") == "online"
                    else '<span class="mode-badge-offline">🟡 Offline</span>'
                )
                content = msg["content"].replace("\n", "<br>")
                st.markdown(
                    f'<div class="{mode_class}">{badge} 🤖<br>{content}</div>',
                    unsafe_allow_html=True
                )
                if msg.get("complaint_id"):
                    st.markdown(
                        f'<div class="complaint-id">📋 Complaint ID: {msg["complaint_id"]}</div>',
                        unsafe_allow_html=True
                    )

    # Input box
    pending = st.session_state.pop("_pending_message", None)
    user_input = st.chat_input(
        "Road ke baare mein poochiye... (Hindi/English)" if st.session_state.lang == "hi"
        else "Ask about any road, budget, or complaint..."
    )
    user_input = user_input or pending

    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get chatbot response
        with st.spinner("Searching road data..."):
            result = chat(user_input)

        # Store for info cards
        st.session_state.last_data   = result.get("data", {})
        st.session_state.last_intent = result.get("intent", "")

        # Add bot message
        st.session_state.messages.append({
            "role":         "assistant",
            "content":      result["response"],
            "mode":         result["mode"],
            "intent":       result["intent"],
            "complaint_id": result.get("complaint_id"),
        })
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# INFO CARDS COLUMN
# ─────────────────────────────────────────────────────────────────────────────

with col_info:
    st.markdown("#### 📄 Details")

    data   = st.session_state.last_data
    intent = st.session_state.last_intent

    if not data:
        st.markdown('<div class="info-card"><h4>Waiting...</h4><p style="color:#888;font-size:0.85rem;">Ask about a road to see details here.</p></div>', unsafe_allow_html=True)

    # ── ROAD INFO CARD ──
    elif intent == "road_lookup" and isinstance(data, dict) and data.get("name"):
        # Road identity
        st.markdown(f"""
        <div class="info-card">
          <h4>🛣️ Road Identity</h4>
          <b>{data['name']}</b><br>
          <span style="color:#888;font-size:0.82rem;">{data.get('road_type','')} • {data.get('state','')} • {data.get('length_km','')} km</span>
        </div>
        """, unsafe_allow_html=True)

        # Contractor card
        score = data.get("accountability_score", 5)
        grade = data.get("contractor_grade", "N/A")
        color = "#00C896" if score >= 7 else "#FFB800" if score >= 5 else "#FF4444"
        bar_w = int((score / 10) * 100)
        st.markdown(f"""
        <div class="info-card">
          <h4>🏗️ Contractor</h4>
          <b>{data.get('contractor_name','N/A')}</b><br>
          <span style="color:{color};font-weight:600;">{score}/10 — {grade}</span>
          <div class="score-bar-wrap">
            <div class="score-bar-fill" style="width:{bar_w}%;background:{color};"></div>
          </div>
          <span style="color:#888;font-size:0.78rem;">Reg: {data.get('contractor_reg','N/A')}</span>
        </div>
        """, unsafe_allow_html=True)

        # DLP Status
        dlp_active = data.get("dlp_active", False)
        dlp_days   = data.get("dlp_days_remaining", 0)
        dlp_color  = "#00C896" if dlp_active else "#FF4444"
        dlp_text   = f"✅ Active — {dlp_days} days left" if dlp_active else f"❌ Expired — {abs(dlp_days)} days ago"
        st.markdown(f"""
        <div class="info-card">
          <h4>📅 DLP Status</h4>
          <span style="color:{dlp_color};font-weight:600;">{dlp_text}</span><br>
          <span style="color:#888;font-size:0.78rem;">Expiry: {data.get('dlp_expiry_date','N/A')}</span><br>
          <span style="color:#888;font-size:0.78rem;">Last Repair: {data.get('last_repair_date','N/A')}</span>
        </div>
        """, unsafe_allow_html=True)

        # Budget
        util = data.get("budget_utilization_pct", 0)
        util_color = "#00C896" if util >= 90 else "#FFB800" if util >= 70 else "#FF4444"
        st.markdown(f"""
        <div class="info-card">
          <h4>💰 Budget</h4>
          Sanctioned: <b>₹{data.get('budget_sanctioned_cr',0)} Cr</b><br>
          Spent: <b>₹{data.get('budget_spent_cr',0)} Cr</b><br>
          <span style="color:{util_color};font-weight:600;">Utilization: {util}%</span><br>
          <div class="score-bar-wrap">
            <div class="score-bar-fill" style="width:{min(util,100)}%;background:{util_color};"></div>
          </div>
          <span style="color:#888;font-size:0.75rem;">📄 {data.get('funding_source','N/A')}: {data.get('source_document','N/A')}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── BUDGET CARD ──
    elif intent == "budget_query" and isinstance(data, dict) and data.get("budget_sanctioned_cr"):
        util  = data.get("budget_utilization_pct", 0)
        color = "#00C896" if util >= 90 else "#FFB800" if util >= 70 else "#FF4444"
        st.markdown(f"""
        <div class="info-card">
          <h4>💰 Budget Transparency</h4>
          <b>{data.get('name','N/A')}</b><br><br>
          Sanctioned: <b>₹{data.get('budget_sanctioned_cr',0)} Cr</b><br>
          Spent: <b>₹{data.get('budget_spent_cr',0)} Cr</b><br>
          Unspent: <b>₹{data.get('budget_unspent_cr',0)} Cr</b><br>
          <span style="color:{color};font-weight:600;">Utilization: {util}%</span>
          <div class="score-bar-wrap">
            <div class="score-bar-fill" style="width:{min(util,100)}%;background:{color};"></div>
          </div>
          <br>
          <b>Funding Source:</b> {data.get('funding_source','N/A')}<br>
          <span style="color:#FFB800;font-size:0.78rem;">📄 Source: {data.get('source_document','N/A')}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── AUTHORITY CARD ──
    elif intent == "complaint_route" and isinstance(data, dict) and data.get("authority_name"):
        st.markdown(f"""
        <div class="info-card">
          <h4>📞 Complaint Authority</h4>
          <b>{data.get('authority_name','N/A')}</b><br>
          <span style="color:#888;font-size:0.82rem;">{data.get('authority_type','')}</span><br><br>
          👤 <b>{data.get('engineer_name','N/A')}</b><br>
          <span style="color:#888;font-size:0.82rem;">{data.get('designation','')}</span><br><br>
          📧 {data.get('email','N/A')}<br>
          📱 {data.get('phone','N/A')}<br><br>
          🏢 <span style="color:#888;font-size:0.78rem;">{data.get('office_address','N/A')}</span><br><br>
          ⏱️ SLA: <b>{data.get('complaint_sla_days',30)} days</b>
        </div>
        """, unsafe_allow_html=True)

    # ── CONTRACTOR LEADERBOARD ──
    elif intent == "contractor_check":
        try:
            contractors = get_all_contractors_ranked()
            st.markdown('<div class="info-card"><h4>🏆 Contractor Leaderboard</h4>', unsafe_allow_html=True)
            for c in contractors:
                score = c["accountability_score"]
                color = "#00C896" if score >= 7 else "#FFB800" if score >= 5 else "#FF4444"
                bar_w = int((score / 10) * 100)
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                  <span style="font-size:0.85rem;font-weight:600;">{c['name'][:22]}</span>
                  <span style="float:right;color:{color};font-weight:700;">{score}</span><br>
                  <div class="score-bar-wrap">
                    <div class="score-bar-fill" style="width:{bar_w}%;background:{color};"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception:
            st.caption("Contractor data unavailable")

# ─────────────────────────────────────────────────────────────────────────────
# MAP COLUMN
# ─────────────────────────────────────────────────────────────────────────────

with col_map:
    st.markdown("#### 🗺️ Road Map")

    data   = st.session_state.last_data
    intent = st.session_state.last_intent

    # Default center: India
    center_lat, center_lon, zoom = 22.5, 78.9, 5

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="CartoDB dark_matter",
    )

    try:
        if intent == "road_lookup" and isinstance(data, dict) and data.get("start_lat"):
            # Draw road line
            start = [data["start_lat"], data["start_lon"]]
            end   = [data["end_lat"],   data["end_lon"]]
            score = data.get("accountability_score", 5)
            line_color = "#00C896" if score >= 7 else "#FFB800" if score >= 5 else "#FF4444"

            folium.PolyLine(
                [start, end],
                color=line_color, weight=4, opacity=0.8,
                tooltip=data.get("name", "Road"),
            ).add_to(m)

            folium.Marker(
                start,
                tooltip=f"Start: {data.get('name','')}",
                icon=folium.Icon(color="orange", icon="road", prefix="fa"),
            ).add_to(m)
            folium.Marker(
                end,
                tooltip=f"End: {data.get('name','')}",
                icon=folium.Icon(color="green", icon="flag", prefix="fa"),
            ).add_to(m)

            m.fit_bounds([start, end])

        elif intent in ("complaint_route", "complaint_report") and isinstance(data, dict):
            # Show authority location (state capital approx)
            state_coords = {
                "Madhya Pradesh": [23.2599, 77.4126],
                "Maharashtra":    [18.5204, 73.8567],
                "Uttar Pradesh":  [26.8467, 80.9462],
                "Rajasthan":      [26.9124, 75.7873],
                "Tamil Nadu":     [13.0827, 80.2707],
                "Delhi":          [28.6139, 77.2090],
            }
            state = data.get("state")
            if state and state in state_coords:
                loc = state_coords[state]
                folium.Marker(
                    loc,
                    tooltip=data.get("authority_name", "Authority"),
                    icon=folium.Icon(color="red", icon="building", prefix="fa"),
                    popup=folium.Popup(
                        f"<b>{data.get('authority_name','')}</b><br>"
                        f"{data.get('engineer_name','')}<br>"
                        f"{data.get('phone','')}",
                        max_width=200,
                    ),
                ).add_to(m)
                m.location = loc
                m.zoom_start = 8

        else:
            # Default: show all roads in DB
            try:
                all_roads = search_road_flexible("")
                for r in all_roads[:10]:
                    if r.get("contractor_name"):
                        folium.CircleMarker(
                            location=[22.5, 78.9],
                            radius=5,
                            color="#FF6B35",
                            fill=True,
                            tooltip=r.get("name", "Road"),
                        ).add_to(m)
            except Exception:
                pass

    except Exception:
        pass

    st_folium(m, width=None, height=380)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center;margin-top:1rem;color:#444;font-size:0.75rem;">
  SadakWatch AI — IIT Madras Road Safety Hackathon 2026 |
  Data: PMGSY OMMAS · NHAI · CAG Reports · iRAD/eDAR |
  Built for CoERS, MoRTH
</div>
""", unsafe_allow_html=True)