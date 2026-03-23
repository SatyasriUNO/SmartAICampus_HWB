import requests
import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv

# ── 1. INITIAL SETUP ──
load_dotenv()

st.set_page_config(layout="wide", page_title="Smart Campus", page_icon="🎓")

# ── 2. SESSION STATE ──
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "theme" not in st.session_state: st.session_state.theme = "dark"
if "chat_open" not in st.session_state: st.session_state.chat_open = False
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False
if "student_id" not in st.session_state: st.session_state.student_id = "student-001"
if "api_recs" not in st.session_state: st.session_state.api_recs = []
if "reminder_data" not in st.session_state: st.session_state.reminder_data = {}

profile_defaults = {
    "u_name": "Aditi", "u_usn": "1RV22EC001", "u_branch": "ECE",
    "u_sem": "5th", "u_email": "aditi@example.com",
    "u_achieve": "SIH 2025 Winner, Drone Specialist",
    "u_interests": "AI, Robotics, Drones, FinTech, UI/UX"
}
for key, val in profile_defaults.items():
    if key not in st.session_state: st.session_state[key] = val

# ── 3. THEME & STYLING ──
def apply_theme():
    if st.session_state.theme == "dark":
        bg, card, text, accent, btn_bg = "#000000", "#1C1C1E", "#FFFFFF", "#3B82F6", "#434378"
    else:
        bg, card, text, accent, btn_bg = "#BFD5DC", "#FFFFFF", "#5656D8", "#007AFF", "#E5E5EA"

    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; color: {text} !important; }}
    header, footer {{ visibility: hidden; }}

    .card {{ background:{card}; padding:18px; border-radius:18px; border: 1px solid {accent}22; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}

    .notif-box {{ padding: 15px; border-radius: 12px; margin-bottom: 15px; border-left: 6px solid; }}
    .notif-remind {{ background: rgba(59, 130, 246, 0.1); border-color: #3B82F6; }}
    .notif-warning {{ background: rgba(255, 59, 48, 0.1); border-color: #FF3B30; color: #FF3B30; }}

    .manthan-container {{
        background: linear-gradient(135deg, #1e1e2f 0%, {accent} 100%);
        padding: 25px; border-radius: 15px; margin-bottom: 30px; color: white;
    }}

    .profile-wrap {{ position: relative; display: inline-block; }}
    .badge-notif {{ position: absolute; top: -2px; right: -2px; background: #FF3B30; color: white; border-radius: 50%; padding: 2px 7px; font-size: 11px; font-weight: bold; border: 2px solid {bg}; }}

    .title-sec {{ font-size:24px; font-weight: bold; color: {accent}; margin: 20px 0; text-transform: uppercase; letter-spacing: 1px; }}

    .interest-pill {{
        display: inline-block;
        padding: 8px 16px;
        border-radius: 30px;
        margin: 5px;
        font-weight: 600;
        color: white;
        font-size: 13px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# ── 4. TOP PANEL ──
col_title, col_bulb, col_prof = st.columns([0.7, 0.1, 0.2], vertical_alignment="center")

with col_title:
    st.markdown('<h1 style="margin:0;">🎓 Smart Campus</h1>', unsafe_allow_html=True)
    student_options = {
        "Arjun (Tech)": "student-001",
        "Priya (Arts)": "student-002",
        "Rahul (Fresher)": "student-003"
    }
    selected = st.selectbox(
        "Student",
        options=list(student_options.keys()),
        label_visibility="collapsed"
    )
    # Reset chat when switching students
    if st.session_state.student_id != student_options[selected]:
        st.session_state.chat_history = []
        st.session_state.api_recs = []
        st.session_state.reminder_data = {}
    st.session_state.student_id = student_options[selected]

with col_bulb:
    if st.button("💡", help="Toggle Theme"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

with col_prof:
    c1, c2 = st.columns([0.4, 0.6])
    with c1:
        if st.button("👤", key="avatar_main"):
            st.session_state.page = "Profile"
            st.rerun()
    with c2:
        st.markdown(f'''<div class="profile-wrap" style="margin-top:-45px; pointer-events:none;">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="50" height="50" style="border-radius:50%; border: 2px solid #3B82F6;">
            <span class="badge-notif">2</span>
        </div>''', unsafe_allow_html=True)

# Navigation
nav_cols = st.columns(4)
if nav_cols[0].button("Dashboard", use_container_width=True): st.session_state.page = "Dashboard"
if nav_cols[1].button("Interests", use_container_width=True): st.session_state.page = "Interests"
if nav_cols[2].button("Map Radar", use_container_width=True): st.session_state.page = "Map"
if nav_cols[3].button("Registrations", use_container_width=True): st.session_state.page = "Registrations"

st.divider()

# ── 5. FETCH REMINDERS FROM API (once per page load, on Dashboard) ──
# FIX: API calls moved HERE (Dashboard level) — NOT inside the chat handler
if st.session_state.page == "Dashboard":
    try:
        rem_res = requests.get(
            f"http://127.0.0.1:8000/reminders/{st.session_state.student_id}",
            timeout=5
        )
        if rem_res.status_code == 200:
            st.session_state.reminder_data = rem_res.json()
    except Exception:
        pass  # backend offline — use static fallback

    try:
        rec_res = requests.get(
            f"http://127.0.0.1:8000/recommendations/{st.session_state.student_id}",
            timeout=5
        )
        if rec_res.status_code == 200:
            st.session_state.api_recs = rec_res.json().get("recommendations", [])
    except Exception:
        pass  # backend offline — use static fallback

# ── 6. PAGES ──
if st.session_state.page == "Dashboard":

    # ── Reminder banner (real API or static fallback) ──
    reminder_data = st.session_state.reminder_data
    cascade = reminder_data.get("cascade", {})
    summary = reminder_data.get("summary", "")

    if cascade.get("detected"):
        st.markdown(
            f'<div class="notif-box notif-warning">🚨 <b>{cascade.get("alert", "Deadline collision detected!")}</b></div>',
            unsafe_allow_html=True
        )
    elif summary:
        st.markdown(
            f'<div class="notif-box notif-remind">🔔 {summary}</div>',
            unsafe_allow_html=True
        )
    else:
        # Static fallback if backend is offline
        st.markdown(
            '<div class="notif-box notif-remind">🔔 <b>REMINDER:</b> Ideathon Registration closes at 6:00 PM today!</div>',
            unsafe_allow_html=True
        )

    st.markdown(f"""
    <div class="manthan-container">
        <h2 style="margin:0; color:white;">🧠 MANTHAN</h2>
        <p style="font-size:1.1em; opacity:0.9;">
            <b>🔮 Hindsight Intelligence:</b> Based on your recent focus in <b>{st.session_state.u_interests.split(',')[0]}</b>,
            you are evolving towards <b>Advanced Robotics</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="title-sec">📅 UPCOMING EVENTS</div>', unsafe_allow_html=True)
    e_cols = st.columns(3)

    # Use API recommendations if available, else static fallback
    api_recs = st.session_state.api_recs
    if api_recs:
        for i, rec in enumerate(api_recs[:3]):
            with e_cols[i]:
                st.markdown(f"""<div class="card">
                    <b>{rec.get('event_name', 'Event')}</b><br>
                    🏷️ {rec.get('category', '').capitalize()}<br>
                    📍 {rec.get('location', 'Campus')}<br>
                    <small style="opacity:0.7;">{rec.get('reason', '')}</small>
                </div>""", unsafe_allow_html=True)
    else:
        # Static fallback events
        events = [
            ("GDG Hackathon", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400", "10:00 AM", "Auditorium"),
            ("TedX Talk", "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=400", "02:00 PM", "SMV block seminar hall 01"),
            ("Drone Meet", "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=400", "05:00 PM", "DKM Block room 001")
        ]
        for i, (name, img, time, location) in enumerate(events):
            with e_cols[i]:
                st.markdown(f"""<div class="card">
                    <img src="{img}" style="width:100%; border-radius:10px; height:140px; object-fit:cover; margin-bottom:10px;">
                    <b>{name}</b><br>⏰ {time}<br><b>{location}</b>
                </div>""", unsafe_allow_html=True)

elif st.session_state.page == "Profile":
    col_p1, col_p2 = st.columns([0.8, 0.2])
    with col_p1: st.markdown('<div class="title-sec">👤 USER PROFILE</div>', unsafe_allow_html=True)
    with col_p2:
        if st.button("✎", help="Edit Profile"):
            st.session_state.edit_mode = not st.session_state.edit_mode

    if st.session_state.edit_mode:
        with st.form("edit_profile"):
            st.session_state.u_name = st.text_input("Full Name", st.session_state.u_name)
            st.session_state.u_usn = st.text_input("USN No", st.session_state.u_usn)
            st.session_state.u_branch = st.text_input("Branch", st.session_state.u_branch)
            st.session_state.u_sem = st.selectbox("Semester", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"], index=4)
            st.session_state.u_achieve = st.text_area("Achievements", st.session_state.u_achieve)
            if st.form_submit_button("Save Changes"):
                st.session_state.edit_mode = False
                st.rerun()
    else:
        st.markdown(f"""<div class="card">
            <h3>{st.session_state.u_name}</h3>
            <p><b>🆔 USN:</b> {st.session_state.u_usn}</p>
            <p><b>📚 Branch:</b> {st.session_state.u_branch}</p>
            <p><b>🗓️ Semester:</b> {st.session_state.u_sem}</p>
            <p><b>🏆 Achievements:</b> {st.session_state.u_achieve}</p>
            <p><b>🎯 Interests:</b> {st.session_state.u_interests}</p>
        </div>""", unsafe_allow_html=True)

    if st.button("← Back"): st.session_state.page = "Dashboard"; st.rerun()

elif st.session_state.page == "Map":
    st.markdown('<div class="title-sec">🗺️ CAMPUS RADAR</div>', unsafe_allow_html=True)
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown('<div class="card"><b>📍 Indoor Navigation</b>', unsafe_allow_html=True)
        if os.path.exists("basketball.png"):
            st.image("basketball.png", caption="Campus Floor Plan", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown('<div class="card"><b>🌍 Live GPS Location</b>', unsafe_allow_html=True)
        st.map(pd.DataFrame({'lat': [13.0125], 'lon': [77.7052]}))
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Interests":
    st.markdown('<div class="title-sec">🎯 MANTHAN INTELLIGENCE ADAPTATION</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    colors = ["#3B82F6", "#8B5CF6", "#EC4899", "#F59E0B", "#10B981", "#06B6D4"]
    ints = st.session_state.u_interests.split(',')

    html_pills = ""
    for i, interest in enumerate(ints):
        if interest.strip():
            c = colors[i % len(colors)]
            html_pills += f'<span class="interest-pill" style="background:{c}">{interest.strip()}</span>'

    st.markdown(html_pills, unsafe_allow_html=True)
    st.markdown('<p style="margin-top:20px; opacity:0.8;">Your interests are used by <b>Manthan AI</b> to suggest relevant hackathons.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.u_interests = st.text_area("Update your interests (commas)", st.session_state.u_interests)
    if st.button("Sync Memory"):
        st.toast("Hindsight Synced!")
        st.rerun()

# ── 7. FLOATING CHATBOT ──
st.markdown('<div class="chat-float">', unsafe_allow_html=True)
if st.button("💬", key="chat_tog_btn"):
    st.session_state.chat_open = not st.session_state.chat_open
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.chat_open:
    with st.container():
        st.markdown('<div class="chat-window">', unsafe_allow_html=True)
        st.markdown("<h4 style='padding:15px; margin:0; border-bottom:1px solid #ddd;'>💬 Manthan AI</h4>", unsafe_allow_html=True)

        c_hist = st.container(height=300)
        with c_hist:
            for m in st.session_state.chat_history:
                st.chat_message(m["role"]).write(m["content"])

        if p := st.chat_input("Ask Manthan..."):
            st.session_state.chat_history.append({"role": "user", "content": p})

            # ── CALL BACKEND /chat ──
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={
                        "student_id": st.session_state.student_id,
                        "message": p
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    ans = response.json().get("message", "No answer found.")
                else:
                    ans = f"Backend error: {response.status_code}"
            except Exception as e:
                ans = f"Backend offline. Start server with: python main.py\n(Error: {e})"

            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
